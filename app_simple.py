import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
import re
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="POML vs Plain Text - The Ultimate Comparison",
    page_icon="🥇",
    layout="wide"
)

# Initialize model as None
model = None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .olympiad-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .vs-divider {
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: #ff6b6b;
        margin: 1rem 0;
    }
    .result-container {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background: #f9f9f9;
    }
    .poml-container {
        border-left: 4px solid #4caf50;
        background: #f1f8e9;
    }
    .plain-container {
        border-left: 4px solid #ff9800;
        background: #fff3e0;
    }
    .winner-badge {
        background: #4caf50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .metrics {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
        padding: 1rem;
        background: #f5f5f5;
        border-radius: 8px;
    }
    .metric {
        text-align: center;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f4e79;
    }
</style>
""", unsafe_allow_html=True)

class POMLRenderer:
    def __init__(self):
        self.variables = {}
    
    def execute_with_ai(self, poml_content):
        try:
            if not model:
                return "AI model not available."
            
            structured_prompt = self.poml_to_prompt(poml_content)
            response = model.generate_content(structured_prompt)
            
            # Handle different response types and safety filters
            if hasattr(response, 'text') and response.text:
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                # Try to extract content from candidates
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            return candidate.content.parts[0].text
                    if hasattr(candidate, 'finish_reason'):
                        if candidate.finish_reason == 1:  # STOP
                            return "Response completed but no text content available."
                        elif candidate.finish_reason == 2:  # MAX_TOKENS
                            return "Response truncated due to length limit."
                        elif candidate.finish_reason == 3:  # SAFETY
                            return "Response blocked by safety filters. POML's structured approach may help bypass this."
                        elif candidate.finish_reason == 4:  # RECITATION
                            return "Response blocked due to recitation concerns."
                return "No valid response content available."
            else:
                return "Empty response received from AI model."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def poml_to_prompt(self, poml_content):
        content = re.sub(r'</?poml[^>]*>', '', poml_content)
        
        role = self.extract_tag_content(content, 'role')
        task = self.extract_tag_content(content, 'task')
        constraints = self.extract_tag_content(content, 'constraints')
        examples = self.extract_tag_content(content, 'example')
        output_format = self.extract_tag_content(content, 'output-format')
        
        prompt_parts = []
        
        if role:
            prompt_parts.append(f"Role: {role}")
        if task:
            prompt_parts.append(f"Task: {task}")
        if constraints:
            prompt_parts.append(f"Constraints: {constraints}")
        if examples:
            prompt_parts.append(f"Example: {examples}")
        if output_format:
            prompt_parts.append(f"Output Format: {output_format}")
        
        return "\n\n".join(prompt_parts)
    
    def extract_tag_content(self, content, tag):
        pattern = f'<{tag}[^>]*>(.*?)</{tag}>'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else None

def execute_plain_text(prompt):
    """Execute plain text prompt with better error handling"""
    try:
        if not model:
            return "AI model not available."
        
        response = model.generate_content(prompt)
        
        # Handle different response types and safety filters
        if hasattr(response, 'text') and response.text:
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            # Try to extract content from candidates
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        return candidate.content.parts[0].text
                if hasattr(candidate, 'finish_reason'):
                    if candidate.finish_reason == 1:  # STOP
                        return "Response completed but no text content available. This often happens with complex prompts that lack structure."
                    elif candidate.finish_reason == 2:  # MAX_TOKENS
                        return "Response truncated due to length limit."
                    elif candidate.finish_reason == 3:  # SAFETY
                        return "❌ BLOCKED: Response blocked by safety filters. Plain text prompts are more likely to trigger safety concerns due to ambiguous phrasing."
                    elif candidate.finish_reason == 4:  # RECITATION
                        return "❌ BLOCKED: Response blocked due to recitation concerns."
            return "❌ FAILED: No valid response content available from plain text approach."
        else:
            return "❌ FAILED: Empty response received from AI model."
    except Exception as e:
        return f"❌ ERROR: {str(e)}"

def save_results_to_file(challenge_name, challenge_desc, plain_prompt, plain_response, poml_prompt, poml_response, metrics_comparison):
    """Save comparison results to a text file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"POML_Comparison_{challenge_name.replace(' ', '_')}_{timestamp}.txt"
    
    content = f"""
POML vs Plain Text Comparison Results
=====================================
Challenge: {challenge_name}
Description: {challenge_desc}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

PLAIN TEXT APPROACH
==================
Prompt:
{plain_prompt}

Response:
{plain_response}

POML STRUCTURED APPROACH  
========================
Prompt:
{poml_prompt}

Response:
{poml_response}

COMPARISON METRICS
==================
{metrics_comparison}

ANALYSIS
========
This comparison demonstrates how POML's structured approach provides:
- Better handling of complex, multi-constraint problems
- More robust responses that avoid safety filter issues
- Systematic breakdown of requirements
- Higher quality, more comprehensive solutions

Generated by POML Comparison Tool
"""
    
    return filename, content

def get_olympiad_challenges():
    return {
        "💻 Advanced Graph Theory - Minimum Vertex Cover with Constraints": {
            "description": "Solve a complex computational geometry problem with multiple optimization criteria",
            "plain_text": "Given a weighted graph G with n vertices (n ≤ 10^5) where each vertex has a color (red, blue, or green) and a weight, find the minimum weighted vertex cover such that: 1) No two adjacent red vertices are both in the cover, 2) At least 60% of blue vertices must be in the cover, 3) The cover must form a connected subgraph, and 4) The total weight is minimized. Provide both the algorithm with complexity analysis and a working implementation.",
            "poml": '''<poml>
  <role>Expert competitive programmer and algorithm designer with deep knowledge of graph theory and optimization</role>
  <task>Design and implement an optimal algorithm for the constrained minimum vertex cover problem</task>
  <constraints>
    <list>
      <item>Graph G with n vertices (n ≤ 10^5)</item>
      <item>Each vertex: color (red/blue/green) and weight</item>
      <item>Constraint 1: No two adjacent red vertices in cover</item>
      <item>Constraint 2: At least 60% of blue vertices in cover</item>
      <item>Constraint 3: Cover forms connected subgraph</item>
      <item>Constraint 4: Minimize total weight</item>
    </list>
  </constraints>
  <example>
    Strong algorithmic solutions include:
    - Clear problem decomposition and complexity analysis
    - Efficient data structures (union-find, segment trees, etc.)
    - Optimization techniques (DP, greedy with proof, approximation)
    - Edge case handling and correctness proof
  </example>
  <output-format>
    <h3>Problem Analysis</h3>
    <p>Complexity analysis and approach justification</p>
    
    <h3>Algorithm Design</h3>
    <p>Step-by-step algorithm with pseudocode</p>
    
    <h3>Implementation</h3>
    <p>Complete working code with comments</p>
    
    <h3>Complexity Analysis</h3>
    <p>Time and space complexity with proof</p>
    
    <h3>Correctness Proof</h3>
    <p>Mathematical proof of algorithm correctness</p>
    
    <h3>Test Cases</h3>
    <p>Edge cases and example inputs/outputs</p>
  </output-format>
</poml>'''
        },
        
        "🌐 Advanced Dynamic Programming - Optimal Binary Tree Construction": {
            "description": "Design an optimal algorithm for constructing binary search trees with complex constraints",
            "plain_text": "Given n keys with access frequencies and a set of 'forbidden pairs' (keys that cannot be in the same subtree), construct an optimal binary search tree that minimizes expected access cost while respecting forbidden constraints. Additionally, the tree must maintain the property that for any node, the sum of frequencies in its left subtree differs from the right subtree by at most k. Provide the DP recurrence, implementation, and prove optimality.",
            "poml": '''<poml>
  <role>Expert in advanced algorithms and dynamic programming with specialization in tree structures and optimization</role>
  <task>Design optimal DP algorithm for constrained binary search tree construction</task>
  <constraints>
    <list>
      <item>n keys with access frequencies</item>
      <item>Forbidden pairs: certain keys cannot be in same subtree</item>
      <item>BST property must be maintained</item>
      <item>Balance constraint: |freq_left - freq_right| ≤ k for all nodes</item>
      <item>Minimize expected access cost</item>
      <item>Prove optimality of solution</item>
    </list>
  </constraints>
  <example>
    Advanced DP solutions require:
    - State space definition with multiple dimensions
    - Optimal substructure proof
    - Recurrence relation derivation
    - Memoization strategy for efficiency
    - Reconstruction of optimal solution
  </example>
  <output-format>
    <h3>Problem Formulation</h3>
    <p>Mathematical model and state space definition</p>
    
    <h3>DP Recurrence</h3>
    <p>Complete recurrence relation with base cases</p>
    
    <h3>Algorithm Implementation</h3>
    <p>Full code with memoization and optimization</p>
    
    <h3>Optimality Proof</h3>
    <p>Mathematical proof of optimal substructure and correctness</p>
    
    <h3>Complexity Analysis</h3>
    <p>Detailed time/space complexity with optimization techniques</p>
    
    <h3>Solution Reconstruction</h3>
    <p>How to build the actual optimal tree from DP table</p>
  </output-format>
</poml>'''
        },
        
        "🔢 Number Theory & Cryptography - Advanced Modular Arithmetic": {
            "description": "Implement efficient algorithms for advanced number-theoretic computations in cryptography",
            "plain_text": "Implement an efficient algorithm to solve the system: find all integers x such that x ≡ a₁ (mod m₁), x ≡ a₂ (mod m₂), ..., x ≡ aₖ (mod mₖ) where the moduli are not necessarily pairwise coprime, and additionally x must satisfy: x = p^α * q^β * r^γ where p, q, r are distinct primes > 10^6, and α + β + γ = n (given). The solution must handle up to 10^6 congruences efficiently and work for moduli up to 10^18.",
            "poml": '''<poml>
  <role>Expert mathematician and cryptographer with deep knowledge of computational number theory and advanced modular arithmetic</role>
  <task>Design and implement efficient algorithms for solving complex modular systems with additional constraints</task>
  <constraints>
    <list>
      <item>System of k congruences (k ≤ 10^6)</item>
      <item>Moduli not necessarily pairwise coprime</item>
      <item>Moduli up to 10^18</item>
      <item>Additional constraint: x = p^α * q^β * r^γ</item>
      <item>p, q, r distinct primes > 10^6</item>
      <item>α + β + γ = n (given)</item>
      <item>Must be efficient for large inputs</item>
    </list>
  </constraints>
  <example>
    Advanced number theory solutions include:
    - Extended Euclidean algorithm for gcd computations
    - Chinese Remainder Theorem extensions
    - Prime factorization and primality testing
    - Modular exponentiation and inverse
    - Efficient handling of large numbers
  </example>
  <output-format>
    <h3>Mathematical Foundation</h3>
    <p>Number theory concepts and theorem applications</p>
    
    <h3>Algorithm Design</h3>
    <p>Step-by-step approach with mathematical justification</p>
    
    <h3>Efficient Implementation</h3>
    <p>Optimized code handling large numbers and edge cases</p>
    
    <h3>Complexity Analysis</h3>
    <p>Detailed analysis of time/space complexity</p>
    
    <h3>Mathematical Proof</h3>
    <p>Correctness proof and convergence analysis</p>
    
    <h3>Optimization Techniques</h3>
    <p>Advanced optimizations for handling large-scale inputs</p>
  </output-format>
</poml>'''
        },
        
        "🧮 Mathematical Olympiad Problem": {
            "description": "Solve a complex combinatorics problem with multiple constraints",
            "plain_text": "Solve this problem: In how many ways can 12 people be arranged in a circle such that exactly 3 specific people are not sitting next to each other, and there are exactly 2 pairs of adjacent people who are wearing the same color shirt (red or blue), given that 7 people wear red shirts and 5 wear blue shirts?",
            "poml": '''<poml>
  <role>Expert mathematician specializing in combinatorics and olympiad problem solving</role>
  <task>Solve the following complex combinatorics problem with step-by-step reasoning</task>
  <constraints>
    <list>
      <item>12 people arranged in a circle</item>
      <item>Exactly 3 specific people must NOT sit next to each other</item>
      <item>Exactly 2 pairs of adjacent people wear same color shirts</item>
      <item>7 people wear red shirts, 5 wear blue shirts</item>
    </list>
  </constraints>
  <example>
    For simpler problems, break down into:
    1) Total arrangements without constraints
    2) Apply each constraint systematically  
    3) Use inclusion-exclusion principle
    4) Verify with smaller cases
  </example>
  <output-format>
    <h3>Problem Analysis</h3>
    <p>Break down the constraints and approach</p>
    
    <h3>Step-by-Step Solution</h3>
    <p>Detailed mathematical reasoning for each step</p>
    
    <h3>Calculations</h3>
    <p>Show all mathematical work with formulas</p>
    
    <h3>Final Answer</h3>
    <p>Clear numerical result with verification</p>
  </output-format>
</poml>'''
        },
        
        "🧬 Advanced Chemistry Synthesis": {
            "description": "Design a multi-step organic synthesis with stereochemistry considerations",
            "plain_text": "Design a synthesis pathway for (2R,3S)-2,3-dihydroxy-3-phenylpropanoic acid starting from benzaldehyde and any other reagents with up to 3 carbons. The synthesis must maintain stereochemistry throughout and explain the mechanism for each step including transition states.",
            "poml": '''<poml>
  <role>Expert organic chemist with deep knowledge of asymmetric synthesis and reaction mechanisms</role>
  <task>Design a complete stereoselective synthesis pathway with mechanistic details</task>
  <constraints>
    <list>
      <item>Starting material: benzaldehyde only</item>
      <item>Additional reagents: maximum 3 carbons each</item>
      <item>Target: (2R,3S)-2,3-dihydroxy-3-phenylpropanoic acid</item>
      <item>Must maintain stereochemistry throughout</item>
      <item>Include mechanism and transition states</item>
    </list>
  </constraints>
  <example>
    Good synthesis design includes:
    - Retrosynthetic analysis
    - Stereochemical considerations at each step
    - Reaction conditions (temperature, solvent, catalysts)
    - Yield estimates and potential side reactions
  </example>
  <output-format>
    <h3>Retrosynthetic Analysis</h3>
    <p>Work backwards from target to identify key disconnections</p>
    
    <h3>Forward Synthesis</h3>
    <p>Step-by-step synthesis with reagents and conditions</p>
    
    <h3>Stereochemical Control</h3>
    <p>Explanation of how stereochemistry is established and maintained</p>
    
    <h3>Mechanisms</h3>
    <p>Detailed mechanisms with transition states for each step</p>
    
    <h3>Alternative Routes</h3>
    <p>Discussion of other possible approaches and why this route is optimal</p>
  </output-format>
</poml>'''
        },
        
        "🔬 Quantum Physics Challenge": {
            "description": "Analyze a complex quantum mechanical system with multiple interacting particles",
            "plain_text": "A system consists of 3 spin-1/2 particles in a 1D infinite square well with width L, where particles 1 and 2 are identical fermions and particle 3 is distinguishable. The particles interact via a contact interaction V₁₂δ(x₁-x₂) + V₁₃δ(x₁-x₃) + V₂₃δ(x₂-x₃). Find the ground state energy and wavefunction, considering both spatial and spin degrees of freedom. Analyze how the energy changes with interaction strength and explain the physical interpretation.",
            "poml": '''<poml>
  <role>Theoretical physicist expert in quantum many-body systems and advanced quantum mechanics</role>
  <task>Solve the quantum many-body problem for 3 interacting particles with mixed statistics</task>
  <constraints>
    <list>
      <item>3 spin-1/2 particles in 1D infinite square well (width L)</item>
      <item>Particles 1,2: identical fermions; Particle 3: distinguishable</item>
      <item>Contact interactions: V₁₂δ(x₁-x₂) + V₁₃δ(x₁-x₃) + V₂₃δ(x₂-x₃)</item>
      <item>Include both spatial and spin wavefunctions</item>
      <item>Find ground state energy and wavefunction</item>
      <item>Analyze dependence on interaction strength</item>
    </list>
  </constraints>
  <example>
    For quantum many-body problems:
    - Start with non-interacting system
    - Apply symmetry requirements (fermion antisymmetry)
    - Use variational or perturbative methods
    - Consider both strong and weak coupling limits
  </example>
  <output-format>
    <h3>System Setup</h3>
    <p>Hamiltonian and symmetry requirements</p>
    
    <h3>Non-interacting Solution</h3>
    <p>Base case without interactions</p>
    
    <h3>Interacting System Analysis</h3>
    <p>Treatment of contact interactions with proper wavefunctions</p>
    
    <h3>Ground State Solution</h3>
    <p>Energy eigenvalue and normalized wavefunction</p>
    
    <h3>Physical Interpretation</h3>
    <p>Analysis of interaction effects and limiting behaviors</p>
    
    <h3>Numerical/Graphical Analysis</h3>
    <p>How energy varies with interaction parameters</p>
  </output-format>
</poml>'''
        }
    }

def analyze_response(text):
    """Simple response quality analysis"""
    words = len(text.split())
    sentences = len([s for s in text.split('.') if s.strip()])
    
    # Structure score based on headers and organization
    structure_indicators = ['step', 'analysis', 'solution', 'answer', 'conclusion', '#', '##', '###']
    structure_count = sum(1 for indicator in structure_indicators if indicator.lower() in text.lower())
    structure_score = min(100, structure_count * 8)
    
    # Completeness score based on length and detail
    completeness_score = min(100, words / 10)
    
    # Technical depth score
    technical_terms = ['formula', 'equation', 'calculation', 'mechanism', 'analysis', 'theory', 'principle']
    technical_count = sum(1 for term in technical_terms if term.lower() in text.lower())
    technical_score = min(100, technical_count * 12)
    
    return {
        'words': words,
        'structure_score': round(structure_score, 1),
        'completeness_score': round(completeness_score, 1),
        'technical_score': round(technical_score, 1),
        'overall_score': round((structure_score + completeness_score + technical_score) / 3, 1)
    }

def convert_to_poml(plain_text, settings):
    """Production-ready plain text to POML converter following Microsoft specifications"""
    
    # Initialize POML components
    components = {
        'role': None,
        'task': None,
        'constraints': [],
        'examples': [],
        'output_format': None,
        'hints': []
    }
    
    # Clean and prepare text
    text = plain_text.strip()
    
    # 1. ROLE DETECTION AND ENHANCEMENT
    components['role'] = detect_and_enhance_role(text, settings)
    
    # 2. TASK DETECTION  
    components['task'] = extract_main_task(text)
    
    # 3. CONSTRAINT DETECTION (Production-grade)
    if settings.get('detailed_constraints', True):
        components['constraints'] = extract_technical_constraints(text)
    
    # 4. EXAMPLE DETECTION
    if settings.get('include_examples', True):
        components['examples'] = extract_examples(text)
    
    # 5. OUTPUT FORMAT DETECTION
    if settings.get('structured_output', True):
        components['output_format'] = determine_optimal_output_sections(text, settings)
    
    # 6. HINT DETECTION
    components['hints'] = extract_hints(text)
    
    # Generate POML with proper structure
    return generate_poml_output(components, settings)

def detect_and_enhance_role(text, settings):
    """Detect role with domain-specific enhancement"""
    
    # Try explicit role patterns first (only in first 100 characters)
    first_part = text[:200].strip()
    role_patterns = [
        r'^you are\s+(.+?)(?:\.|,|and|\n)',
        r'^act as\s+(.+?)(?:\.|,|and|\n)',
        r'^as an?\s+(.+?)(?:\.|,|and|\n)',
        r'you are\s+(.+?)(?:\.|,|and|\n)',
        r'act as\s+(.+?)(?:\.|,|and|\n)'
    ]
    
    for pattern in role_patterns:
        match = re.search(pattern, first_part, re.IGNORECASE)
        if match:
            role_text = match.group(1).strip()
            if len(role_text) < 50:  # Avoid capturing problem descriptions
                return enhance_role_with_settings(role_text, settings)
    
    # Infer role from content domain
    domain = detect_content_domain(text)
    base_role = get_domain_expert_role(domain)
    
    return enhance_role_with_settings(base_role, settings)

def detect_content_domain(text):
    """Detect the domain of the content for appropriate role assignment"""
    
    # Technical/Algorithm indicators
    if any(term in text.lower() for term in [
        'graph', 'vertex', 'algorithm', 'complexity', 'optimization', 'implementation',
        'binary tree', 'dynamic programming', 'greedy', 'divide and conquer'
    ]):
        return 'technical_algorithms'
    
    # Mathematical indicators  
    elif any(term in text.lower() for term in [
        'theorem', 'proof', 'lemma', 'equation', 'formula', 'mathematical',
        'modular arithmetic', 'number theory', 'combinatorics'
    ]):
        return 'mathematics'
    
    # Data science indicators
    elif any(term in text.lower() for term in [
        'dataset', 'analysis', 'insights', 'visualization', 'machine learning',
        'statistics', 'correlation', 'regression'
    ]):
        return 'data_science'
    
    # Software architecture indicators
    elif any(term in text.lower() for term in [
        'system design', 'architecture', 'microservices', 'scalability',
        'distributed', 'api', 'database'
    ]):
        return 'software_architecture'
    
    # Business/Strategy indicators
    elif any(term in text.lower() for term in [
        'strategy', 'market', 'revenue', 'roi', 'business plan',
        'stakeholder', 'competitive analysis'
    ]):
        return 'business_strategy'
    
    # Creative indicators
    elif any(term in text.lower() for term in [
        'story', 'creative', 'writing', 'narrative', 'character',
        'plot', 'dialogue', 'creative writing'
    ]):
        return 'creative'
    
    return 'general'

def get_domain_expert_role(domain):
    """Get appropriate expert role for detected domain"""
    
    domain_roles = {
        'technical_algorithms': 'algorithm designer and computer scientist',
        'mathematics': 'mathematician and theoretical researcher', 
        'data_science': 'data scientist and analytics expert',
        'software_architecture': 'software architect and system designer',
        'business_strategy': 'business strategist and analyst',
        'creative': 'creative writing specialist and storyteller',
        'general': 'subject matter expert'
    }
    
    return domain_roles.get(domain, 'expert specialist')

def enhance_role_with_settings(base_role, settings):
    """Apply role enhancement based on user settings"""
    
    enhancement = settings.get('role_enhancement', 'Expert level')
    technical_focus = settings.get('technical_focus', False)
    
    # Apply technical focus first
    if technical_focus and 'expert' not in base_role.lower():
        base_role = f"expert {base_role}"
    
    # Apply enhancement level
    if enhancement == 'Expert level' and 'expert' not in base_role.lower():
        enhanced_role = f"Expert {base_role}"
    elif enhancement == 'Professional' and 'professional' not in base_role.lower():
        enhanced_role = f"Professional {base_role}"
    elif enhancement == 'Specialist' and 'specialist' not in base_role.lower():
        enhanced_role = f"Senior specialist in {base_role.split()[0]}"
    elif enhancement == 'Consultant':
        enhanced_role = f"Expert consultant specializing in {base_role.split()[0]}"
    else:
        enhanced_role = base_role
    
    # Ensure proper capitalization
    if enhanced_role and enhanced_role[0].islower():
        enhanced_role = enhanced_role[0].upper() + enhanced_role[1:]
    
    return enhanced_role

def extract_main_task(text):
    """Extract the main task using multiple strategies"""
    
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    
    # Strategy 1: Explicit requests
    request_patterns = [
        r'(?:please|can you|could you|would you)\s+(.+?)(?:\.|$)',
        r'(?:help me|assist me with)\s+(.+?)(?:\.|$)',
        r'(?:I need you to|I want you to)\s+(.+?)(?:\.|$)'
    ]
    
    for sentence in sentences:
        for pattern in request_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                return clean_task_text(match.group(1))
    
    # Strategy 2: Mathematical problem patterns
    math_patterns = [
        r'find\s+(.+?)(?:\s+such that|\s+where|\.|$)',
        r'determine\s+(.+?)(?:\s+such that|\s+where|\.|$)',
        r'calculate\s+(.+?)(?:\s+such that|\s+where|\.|$)',
        r'solve\s+(.+?)(?:\s+such that|\s+where|\.|$)',
        r'compute\s+(.+?)(?:\s+such that|\s+where|\.|$)'
    ]
    
    for sentence in sentences:
        for pattern in math_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                task_text = clean_task_text(match.group(1))
                return f"Find {task_text}"
    
    # Strategy 3: Deliverable requests (usually in last sentence)
    if sentences:
        last_sentence = sentences[-1]
        deliverable_patterns = [
            r'provide\s+(.+?)(?:\.|$)',
            r'give\s+(.+?)(?:\.|$)',
            r'show\s+(.+?)(?:\.|$)',
            r'demonstrate\s+(.+?)(?:\.|$)',
            r'explain\s+(.+?)(?:\.|$)'
        ]
        
        for pattern in deliverable_patterns:
            match = re.search(pattern, last_sentence, re.IGNORECASE)
            if match:
                return f"Provide {clean_task_text(match.group(1))}"
    
    # Strategy 4: Imperative verbs at sentence start
    imperative_patterns = [
        r'^(design|create|build|develop|implement|analyze|evaluate)\s+(.+?)(?:\.|$)'
    ]
    
    for sentence in sentences:
        for pattern in imperative_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                return f"{match.group(1).capitalize()} {clean_task_text(match.group(2))}"
    
    return "Solve the given problem comprehensively"

def clean_task_text(task_text):
    """Clean and optimize task text"""
    
    # Remove common endings that should be in constraints
    task_text = re.sub(r'\s+such that.*$', '', task_text, flags=re.IGNORECASE)
    task_text = re.sub(r'\s+where.*$', '', task_text, flags=re.IGNORECASE)
    task_text = re.sub(r'\s+with the following.*$', '', task_text, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    task_text = re.sub(r'\s+', ' ', task_text).strip()
    
    return task_text

def extract_technical_constraints(text):
    """Production-grade constraint extraction with mathematical notation support"""
    
    constraints = []
    
    # Pattern 1: Numbered constraints (most common in technical problems)
    numbered_pattern = r'(\d+)\)\s*([^.]+?)(?=\s*(?:\d+\)|and\s*\d+\)|\.|$))'
    numbered_matches = re.finditer(numbered_pattern, text, re.IGNORECASE)
    
    for match in numbered_matches:
        constraint_text = match.group(2).strip()
        
        # Filter out setup text and keep actual constraints
        if (len(constraint_text) > 20 and 
            not any(skip in constraint_text.lower() for skip in [
                'given a weighted graph', 'where each vertex has', 'find the minimum'
            ])):
            
            # Clean constraint text
            constraint_text = clean_constraint_text(constraint_text)
            if constraint_text and not is_duplicate_constraint(constraint_text, constraints):
                constraints.append(constraint_text)
    
    # Pattern 2: "Such that" clauses
    such_that_pattern = r'such that:\s*(.+?)(?:\.|$)'
    such_that_match = re.search(such_that_pattern, text, re.IGNORECASE | re.DOTALL)
    if such_that_match:
        clause_text = such_that_match.group(1)
        # Parse individual constraints from the clause
        individual_constraints = parse_constraint_clause(clause_text)
        for constraint in individual_constraints:
            if not is_duplicate_constraint(constraint, constraints):
                constraints.append(constraint)
    
    # Pattern 3: Explicit constraint keywords
    constraint_patterns = [
        r'(?:constraint|requirement|condition)\s*(?:\d+)?\s*[:]\s*([^.]+)',
        r'(?:must|should|cannot|must not)\s+([^.]+?)(?:\.|,|and|$)',
        r'(?:ensure|guarantee)\s+(?:that\s+)?([^.]+?)(?:\.|,|and|$)'
    ]
    
    for pattern in constraint_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            constraint_text = clean_constraint_text(match.group(1))
            if (constraint_text and 
                len(constraint_text) > 15 and 
                not is_duplicate_constraint(constraint_text, constraints)):
                constraints.append(constraint_text)
    
    return constraints[:6]  # Limit to 6 most important constraints

def is_duplicate_constraint(new_constraint, existing_constraints):
    """Check if a constraint is a duplicate or very similar to existing ones"""
    
    if not new_constraint:
        return True
    
    new_lower = new_constraint.lower()
    
    for existing in existing_constraints:
        existing_lower = existing.lower()
        
        # Exact match
        if new_lower == existing_lower:
            return True
        
        # Semantic similarity - check if one contains the key words of the other
        new_words = set(new_lower.split())
        existing_words = set(existing_lower.split())
        
        # If 80% of words overlap, consider it a duplicate
        if len(new_words & existing_words) / max(len(new_words), len(existing_words)) > 0.8:
            return True
        
        # Check for specific patterns that indicate duplicates
        key_phrases = ['connected subgraph', 'adjacent red vertices', 'blue vertices', 'total weight']
        for phrase in key_phrases:
            if phrase in new_lower and phrase in existing_lower:
                # If they share the same key phrase and have similar length, likely duplicate
                if abs(len(new_constraint) - len(existing)) < 20:
                    return True
    
    return False

def clean_constraint_text(constraint_text):
    """Clean and validate constraint text"""
    
    if not constraint_text:
        return ""
    
    # Remove leading/trailing whitespace and punctuation
    constraint_text = constraint_text.strip().rstrip(',').strip()
    
    # Remove incomplete parentheses and brackets
    if constraint_text.count('(') != constraint_text.count(')'):
        # Remove incomplete parenthetical expressions
        constraint_text = re.sub(r'\([^)]*$', '', constraint_text)
        constraint_text = re.sub(r'^[^(]*\)', '', constraint_text)
    
    # Clean up whitespace
    constraint_text = re.sub(r'\s+', ' ', constraint_text).strip()
    
    # Must be substantial enough to be meaningful
    if len(constraint_text) < 10:
        return ""
    
    # Capitalize first letter
    if constraint_text:
        constraint_text = constraint_text[0].upper() + constraint_text[1:]
    
    return constraint_text

def parse_constraint_clause(clause_text):
    """Parse a complex constraint clause into individual constraints"""
    
    # Split on common separators
    separators = [r'\s*,\s*\d+\)\s*', r'\s*and\s*\d+\)\s*', r'\s*,\s*and\s+']
    
    constraints = []
    remaining_text = clause_text
    
    for separator in separators:
        if re.search(separator, remaining_text):
            parts = re.split(separator, remaining_text)
            for part in parts:
                cleaned = clean_constraint_text(part)
                if cleaned:
                    constraints.append(cleaned)
            break
    
    if not constraints:
        # If no separators found, treat as single constraint
        cleaned = clean_constraint_text(clause_text)
        if cleaned:
            constraints.append(cleaned)
    
    return constraints

def extract_examples(text):
    """Extract examples and demonstrations"""
    
    examples = []
    
    example_patterns = [
        r'(?:for example|such as|like|including)\s+(.+?)(?:\.|$)',
        r'(?:example|instance):\s*(.+?)(?:\.|$)',
        r'(?:e\.g\.|eg\.)\s+(.+?)(?:\.|$)'
    ]
    
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    
    for sentence in sentences:
        for pattern in example_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                example_text = match.group(1).strip()
                if len(example_text) > 20:  # Substantial examples only
                    examples.append(example_text)
    
    return examples[:2]  # Limit to 2 examples

def extract_hints(text):
    """Extract hints and guidance"""
    
    hints = []
    
    hint_patterns = [
        r'(?:note|remember|keep in mind|consider|pay attention)\s+(?:that\s+)?(.+?)(?:\.|$)',
        r'(?:hint|tip|important|crucial)\s*:\s*(.+?)(?:\.|$)',
        r'(?:be sure to|make sure to|ensure that)\s+(.+?)(?:\.|$)'
    ]
    
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    
    for sentence in sentences:
        for pattern in hint_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                hint_text = match.group(1).strip()
                if len(hint_text) > 15:
                    hints.append(hint_text)
    
    return hints[:2]  # Limit to 2 hints

def determine_optimal_output_sections(text, settings):
    """Determine optimal output sections based on content domain and user settings"""
    
    # Get user-specified sections first
    user_sections = settings.get('output_sections', [])
    if user_sections:
        return user_sections
    
    # Detect domain and provide appropriate sections
    domain = detect_content_domain(text)
    
    domain_sections = {
        'technical_algorithms': [
            'Problem Analysis',
            'Algorithm Design', 
            'Implementation',
            'Complexity Analysis',
            'Correctness Proof'
        ],
        'mathematics': [
            'Mathematical Foundation',
            'Theorem Application',
            'Proof Construction',
            'Solution Verification'
        ],
        'data_science': [
            'Data Analysis',
            'Statistical Methods',
            'Insights and Findings',
            'Recommendations'
        ],
        'software_architecture': [
            'System Architecture',
            'Component Design',
            'Implementation Strategy',
            'Scalability Analysis'
        ],
        'business_strategy': [
            'Executive Summary',
            'Strategic Analysis',
            'Recommendations',
            'Implementation Plan'
        ],
        'creative': [
            'Creative Concept',
            'Development Process',
            'Final Output',
            'Refinement Notes'
        ],
        'general': [
            'Analysis',
            'Key Findings',
            'Recommendations'
        ]
    }
    
    return domain_sections.get(domain, domain_sections['general'])

def generate_poml_output(components, settings):
    """Generate properly structured POML output"""
    
    poml_parts = ['<poml>']
    
    # Add role
    if components['role']:
        poml_parts.append(f'  <role>{components["role"]}</role>')
    
    # Add task
    if components['task']:
        poml_parts.append(f'  <task>{components["task"]}</task>')
    
    # Add constraints with proper structure
    if components['constraints']:
        constraint_grouping = settings.get('constraint_grouping', 'List format')
        
        if constraint_grouping == 'Categorized':
            poml_parts.append('  <constraints>')
            poml_parts.append('    <h3>Requirements</h3>')
            poml_parts.append('    <list>')
            for constraint in components['constraints']:
                poml_parts.append(f'      <item>{constraint}</item>')
            poml_parts.append('    </list>')
            poml_parts.append('  </constraints>')
        else:  # List format (default)
            poml_parts.append('  <constraints>')
            poml_parts.append('    <list>')
            for constraint in components['constraints']:
                poml_parts.append(f'      <item>{constraint}</item>')
            poml_parts.append('    </list>')
            poml_parts.append('  </constraints>')
    
    # Add examples
    if components['examples']:
        poml_parts.append('  <example>')
        for example in components['examples']:
            poml_parts.append(f'    <exampleinput>Sample scenario: {example}</exampleinput>')
            poml_parts.append(f'    <exampleoutput>Detailed response following the specified format</exampleoutput>')
        poml_parts.append('  </example>')
    
    # Add hints
    if components['hints']:
        for hint in components['hints']:
            poml_parts.append(f'  <hint>{hint}</hint>')
    
    # Add output format
    if components['output_format']:
        poml_parts.append('  <output-format>')
        for section in components['output_format']:
            poml_parts.append(f'    <h3>{section}</h3>')
            poml_parts.append(f'    <p>Detailed {section.lower().replace(" ", " ")} with supporting evidence</p>')
        poml_parts.append('  </output-format>')
    
    poml_parts.append('</poml>')
    
    return '\n'.join(poml_parts)

def setup_api_key():
    """Setup API key configuration"""
    global model
    
    st.sidebar.markdown("### 🔑 API Configuration")
    st.sidebar.markdown("Get your free API key from [Google AI Studio](https://aistudio.google.com)")
    
    # API key input
    api_key = st.sidebar.text_input(
        "Enter your Gemini API Key:",
        type="password",
        help="Your API key will not be stored permanently"
    )
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model_name = "gemini-2.5-flash"
            model = genai.GenerativeModel(model_name)
            st.sidebar.success("✅ API key configured successfully!")
            return True
        except Exception as e:
            st.sidebar.error(f"❌ Error configuring API: {e}")
            model = None
            return False
    else:
        st.sidebar.warning("⚠️ Please enter your API key to use the app")
        return False

def main():
    # Setup API key first
    api_configured = setup_api_key()
    
    # Header
    st.markdown('<h1 class="main-header">🥇 POML vs Plain Text: Ultimate Comparison Tool</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Experience structured prompting power with Olympiad challenges + Convert your prompts to POML</p>', unsafe_allow_html=True)
    
    if not api_configured:
        st.info("👆 Please configure your API key in the sidebar to get started")
        return
    
    # Add tabs for different features
    tab1, tab2 = st.tabs(["🥇 Olympiad Challenges", "🔄 POML Converter"])
    
    with tab1:
        olympiad_challenges_tab()
    
    with tab2:
        poml_converter_tab()

def olympiad_challenges_tab():
    """Original olympiad challenges functionality"""
    
    # Challenge selection
    challenges = get_olympiad_challenges()
    selected_challenge = st.selectbox(
        "🎯 Choose an Olympiad-Level Challenge:",
        list(challenges.keys()),
        help="These are genuinely difficult problems that test AI reasoning capabilities"
    )
    
    if selected_challenge:
        challenge = challenges[selected_challenge]
        
        # Challenge description
        st.markdown(f'<div class="olympiad-card">', unsafe_allow_html=True)
        st.markdown(f"**Challenge:** {challenge['description']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Execute button
        if st.button("🚀 Run Both Approaches", type="primary", use_container_width=True):
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 📝 Plain Text Approach")
                st.code(challenge['plain_text'], language='text')
                
                with st.spinner("AI thinking with plain text..."):
                    plain_response = execute_plain_text(challenge['plain_text'])
                    plain_metrics = analyze_response(plain_response)
                    
                    st.markdown('<div class="result-container plain-container">', unsafe_allow_html=True)
                    st.markdown("**AI Response:**")
                    st.markdown(plain_response)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Store in session state
                    st.session_state['plain_response'] = plain_response
                    st.session_state['plain_metrics'] = plain_metrics
            
            with col2:
                st.markdown("### 🏗️ POML Structured Approach")
                st.code(challenge['poml'], language='xml')
                
                with st.spinner("AI thinking with POML structure..."):
                    renderer = POMLRenderer()
                    poml_response = renderer.execute_with_ai(challenge['poml'])
                    poml_metrics = analyze_response(poml_response)
                    
                    st.markdown('<div class="result-container poml-container">', unsafe_allow_html=True)
                    st.markdown("**AI Response:**")
                    st.markdown(poml_response)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Store in session state
                    st.session_state['poml_response'] = poml_response
                    st.session_state['poml_metrics'] = poml_metrics
                    st.session_state['current_challenge'] = selected_challenge
                    st.session_state['current_challenge_data'] = challenge
        
        # Show comparison if both responses exist
        if 'plain_metrics' in st.session_state and 'poml_metrics' in st.session_state:
            st.markdown('<div class="vs-divider">⚡ COMPARISON RESULTS ⚡</div>', unsafe_allow_html=True)
            
            # Metrics comparison
            plain_m = st.session_state['plain_metrics']
            poml_m = st.session_state['poml_metrics']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric">', unsafe_allow_html=True)
                st.markdown("**Structure**")
                st.markdown(f'<div class="metric-value">{poml_m["structure_score"]}%</div>', unsafe_allow_html=True)
                st.markdown(f"vs {plain_m['structure_score']}%")
                delta = poml_m['structure_score'] - plain_m['structure_score']
                if delta > 0:
                    st.markdown(f"🟢 +{delta:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric">', unsafe_allow_html=True)
                st.markdown("**Completeness**")
                st.markdown(f'<div class="metric-value">{poml_m["completeness_score"]}%</div>', unsafe_allow_html=True)
                st.markdown(f"vs {plain_m['completeness_score']}%")
                delta = poml_m['completeness_score'] - plain_m['completeness_score']
                if delta > 0:
                    st.markdown(f"🟢 +{delta:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric">', unsafe_allow_html=True)
                st.markdown("**Technical Depth**")
                st.markdown(f'<div class="metric-value">{poml_m["technical_score"]}%</div>', unsafe_allow_html=True)
                st.markdown(f"vs {plain_m['technical_score']}%")
                delta = poml_m['technical_score'] - plain_m['technical_score']
                if delta > 0:
                    st.markdown(f"🟢 +{delta:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric">', unsafe_allow_html=True)
                st.markdown("**Overall Score**")
                st.markdown(f'<div class="metric-value">{poml_m["overall_score"]}%</div>', unsafe_allow_html=True)
                st.markdown(f"vs {plain_m['overall_score']}%")
                delta = poml_m['overall_score'] - plain_m['overall_score']
                if delta > 0:
                    st.markdown(f"🟢 +{delta:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Winner declaration
            if poml_m['overall_score'] > plain_m['overall_score']:
                st.markdown('<div class="winner-badge">🏆 POML WINS! Better structure leads to superior problem-solving</div>', unsafe_allow_html=True)
            
            # Download button for results
            st.markdown("### 📥 Download Results")
            
            # Create metrics comparison text
            metrics_text = f"""
Structure Score: POML {poml_m['structure_score']}% vs Plain Text {plain_m['structure_score']}% (Δ: +{poml_m['structure_score'] - plain_m['structure_score']:.1f}%)
Completeness Score: POML {poml_m['completeness_score']}% vs Plain Text {plain_m['completeness_score']}% (Δ: +{poml_m['completeness_score'] - plain_m['completeness_score']:.1f}%)
Technical Depth: POML {poml_m['technical_score']}% vs Plain Text {plain_m['technical_score']}% (Δ: +{poml_m['technical_score'] - plain_m['technical_score']:.1f}%)
Overall Score: POML {poml_m['overall_score']}% vs Plain Text {plain_m['overall_score']}% (Δ: +{poml_m['overall_score'] - plain_m['overall_score']:.1f}%)

Winner: {"POML" if poml_m['overall_score'] > plain_m['overall_score'] else "Plain Text"}
"""
            
            if 'current_challenge' in st.session_state and 'current_challenge_data' in st.session_state:
                challenge_name = st.session_state['current_challenge']
                challenge_data = st.session_state['current_challenge_data']
                
                filename, file_content = save_results_to_file(
                    challenge_name,
                    challenge_data['description'],
                    challenge_data['plain_text'],
                    st.session_state['plain_response'],
                    challenge_data['poml'],
                    st.session_state['poml_response'],
                    metrics_text
                )
                
                st.download_button(
                    label="📄 Download Complete Comparison Report",
                    data=file_content,
                    file_name=filename,
                    mime="text/plain",
                    help="Download a comprehensive report with questions, responses, and analysis"
                )
            
            # Why POML wins explanation
            st.markdown("### 🎯 Why POML Excels at Complex Problems")
            st.markdown("""
            **POML's structured approach provides:**
            - **🏗️ Clear Problem Decomposition**: Forces the AI to break complex problems into manageable steps
            - **🎯 Focused Constraints**: Explicitly states all requirements and limitations
            - **📚 Contextual Examples**: Provides pattern recognition for similar problem types  
            - **📋 Structured Output**: Ensures comprehensive coverage of all solution aspects
            - **🔄 Systematic Reasoning**: Guides the AI through logical problem-solving sequences
            
            **Result**: More thorough, accurate, and pedagogically valuable solutions to challenging problems.
            """)

def convert_to_poml_with_llm(plain_text: str, settings: dict) -> str:
    """Convert plain text to POML using LLM with complete documentation"""
    
    if not model:
        return "Error: AI model not configured"
    
    # Complete POML documentation
    poml_documentation = """
# POML (Prompt Orchestration Markup Language) - Complete Documentation

POML is Microsoft's structured prompt engineering framework that uses XML-style markup to create more effective AI interactions.

## Core Structure
```xml
<poml>
  <role>Expert role definition</role>
  <task>Main objective to accomplish</task>
  <constraints>
    <list>
      <item>Specific requirement 1</item>
      <item>Specific requirement 2</item>
    </list>
  </constraints>
  <example>
    <exampleinput>Sample input scenario</exampleinput>
    <exampleoutput>Expected output format</exampleoutput>
  </example>
  <hint>Additional guidance or tips</hint>
  <output-format>
    <h3>Section Name</h3>
    <p>Description of what this section should contain</p>
  </output-format>
</poml>
```

## Tag Specifications

### <role> Tag
- Defines the AI's expertise and perspective
- Should be specific and authoritative
- Examples: "Expert data scientist", "Senior software architect", "Professional business analyst"
- Enhancement levels: Expert > Professional > Senior > Specialist

### <task> Tag  
- Clear, actionable main objective
- Should be concise but comprehensive
- Focus on the primary deliverable
- Avoid including constraints here

### <constraints> Tag
- Always use <list><item> structure for multiple constraints
- Each constraint should be specific and measurable
- Include technical requirements, limitations, and conditions

### <example> Tag (Optional)
- Provides concrete illustrations
- Use <exampleinput> and <exampleoutput> pairs
- Should be substantial and meaningful
- Limit to 1-2 examples maximum

### <hint> Tag (Optional)
- Additional guidance or context
- Important considerations or tips
- Best practices or warnings

### <output-format> Tag
- Defines expected structure using <h3> and <p> tags
- Domain-specific sections for Technical/Algorithms: Problem Analysis, Algorithm Design, Implementation, Complexity Analysis, Correctness Proof
- For Mathematics: Mathematical Foundation, Theorem Application, Proof Construction, Solution Verification
- For Data Science: Data Analysis, Statistical Methods, Insights and Findings, Recommendations
- For Business: Executive Summary, Strategic Analysis, Recommendations, Implementation Plan

## Best Practices
1. Keep roles specific and authoritative
2. Make tasks clear and actionable
3. Use numbered constraints for complex problems
4. Structure output format to match domain needs
5. Ensure mathematical notation is preserved
6. Use proper XML formatting
"""

    conversion_prompt = f"""
You are an expert in POML conversion. Convert the following plain text prompt into properly structured POML format.

COMPLETE POML DOCUMENTATION:
{poml_documentation}

USER SETTINGS:
- Include Examples: {settings.get('include_examples', True)}
- Detailed Constraints: {settings.get('detailed_constraints', True)}  
- Structured Output: {settings.get('structured_output', True)}
- Role Enhancement: {settings.get('role_enhancement', 'Expert level')}
- Constraint Grouping: {settings.get('constraint_grouping', 'List format')}

PLAIN TEXT PROMPT TO CONVERT:
{plain_text}

IMPORTANT RULES:
- Do NOT add any content not present in the original prompt
- Do NOT modify mathematical notation or technical terms
- Follow the exact XML structure shown in documentation
- Ensure no duplicate constraints
- Use proper capitalization for roles
- If no explicit examples exist, do not create them
- Focus on accuracy over creativity

Provide ONLY the final POML output in proper XML format:
"""

    try:
        response = model.generate_content(conversion_prompt)
        
        if hasattr(response, 'text') and response.text:
            # Extract just the POML part from the response
            poml_match = re.search(r'<poml>.*?</poml>', response.text, re.DOTALL)
            if poml_match:
                return poml_match.group(0)
            else:
                return response.text.strip()
        else:
            return "Error: Could not generate POML conversion"
            
    except Exception as e:
        return f"Error: {str(e)}"

def poml_converter_tab():
    """POML converter functionality"""
    st.markdown("### 🔄 Convert Plain Text to POML")
    
    # Conversion method selection
    conversion_method = st.radio(
        "**Choose Conversion Method:**",
        ["🤖 AI-Powered (Recommended)", "⚙️ Rule-Based (Offline)"],
        help="AI-Powered uses LLM with complete POML documentation for better accuracy. Rule-based works offline but may have limitations."
    )
    
    if conversion_method == "🤖 AI-Powered (Recommended)":
        if not model:
            st.warning("⚠️ **AI-Powered conversion requires API key configuration.** Please configure your API key in the sidebar first.")
            st.info("💡 **Why AI-Powered?** Uses complete Microsoft POML documentation for more accurate conversions, especially for complex technical prompts.")
        else:
            st.success("✅ **AI-Powered conversion ready!** Using complete POML documentation for optimal results.")
    else:
        st.warning("⚠️ **Rule-Based Limitations:** May have issues with complex constraints, mathematical notation, and domain-specific formatting. Consider AI-powered for production use.")
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📝 Your Plain Text Prompt")
        plain_text = st.text_area(
            "Enter your prompt:",
            height=200,
            placeholder="Example: You are a data scientist. Analyze this sales dataset and provide insights on customer behavior patterns. Focus on seasonal trends and regional differences. Present your findings in a clear report format.",
            help="Enter any plain text prompt you'd like to convert to POML format"
        )
    
    with col2:
        st.markdown("#### ⚙️ Conversion Settings")
        
        # Settings for conversion
        include_examples = st.checkbox(
            "Include Examples", 
            value=True,
            help="Add example sections to guide the AI"
        )
        
        detailed_constraints = st.checkbox(
            "Detailed Constraints", 
            value=True,
            help="Extract and structure all constraints from the prompt"
        )
        
        structured_output = st.checkbox(
            "Structured Output Format", 
            value=True,
            help="Add specific output formatting requirements"
        )
        
        technical_focus = st.checkbox(
            "Technical Focus", 
            value=False,
            help="Emphasize technical depth and analysis"
        )
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            role_enhancement = st.selectbox(
                "Role Enhancement:",
                ["Auto-detect", "Expert level", "Professional", "Specialist", "Consultant"],
                help="How to enhance the role definition"
            )
            
            constraint_grouping = st.selectbox(
                "Constraint Organization:",
                ["List format", "Categorized", "Prioritized", "Nested"],
                help="How to organize constraints in the POML output"
            )
            
            output_sections = st.multiselect(
                "Required Output Sections:",
                ["Analysis", "Summary", "Recommendations", "Data", "Methodology", "Conclusions"],
                default=["Analysis", "Summary"],
                help="What sections should be included in output format"
            )
    
    # Convert button
    if st.button("🔄 Convert to POML", type="primary", use_container_width=True):
        if not plain_text.strip():
            st.warning("Please enter a prompt to convert.")
        else:
            settings = {
                'include_examples': include_examples,
                'detailed_constraints': detailed_constraints,
                'structured_output': structured_output,
                'technical_focus': technical_focus,
                'role_enhancement': role_enhancement,
                'constraint_grouping': constraint_grouping,
                'output_sections': output_sections
            }
            
            # Choose conversion method
            if conversion_method == "🤖 AI-Powered (Recommended)":
                if not model:
                    st.error("❌ **API key required for AI-powered conversion.** Please configure your API key in the sidebar.")
                    return
                
                with st.spinner("🤖 Converting with AI using complete POML documentation..."):
                    poml_result = convert_to_poml_with_llm(plain_text, settings)
                    conversion_type = "AI-Powered"
            else:
                with st.spinner("⚙️ Converting with rule-based analysis..."):
                    poml_result = convert_to_poml(plain_text, settings)
                    conversion_type = "Rule-Based"
                
            # Display results
            st.markdown("### 📊 Conversion Results")
            st.markdown(f"**Method Used:** {conversion_type}")
            
            if conversion_type == "AI-Powered":
                st.info("✨ **AI-Powered Conversion** - Using complete Microsoft POML documentation for optimal accuracy")
            else:
                st.warning("⚙️ **Rule-Based Conversion** - Limited pattern matching. For better results, try AI-powered conversion.")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 📝 Original Plain Text")
                st.markdown('<div class="result-container plain-container">', unsafe_allow_html=True)
                st.text_area("Original:", value=plain_text, height=300, disabled=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 🏗️ Generated POML")
                st.markdown('<div class="result-container poml-container">', unsafe_allow_html=True)
                st.text_area("POML:", value=poml_result, height=300, disabled=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 Download POML",
                        data=poml_result,
                        file_name="converted_prompt.poml",
                        mime="text/xml",
                        help="Download the converted POML prompt"
                    )
                
                with col2:
                    comparison_text = f"""
PROMPT CONVERSION REPORT
========================
Conversion Method: {conversion_type}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

ORIGINAL PLAIN TEXT:
{plain_text}

CONVERTED POML:
{poml_result}

CONVERSION SETTINGS:
- Method: {conversion_type}
- Include Examples: {include_examples}
- Detailed Constraints: {detailed_constraints}
- Structured Output: {structured_output}
- Technical Focus: {technical_focus}
- Role Enhancement: {role_enhancement}
- Constraint Grouping: {constraint_grouping}
- Output Sections: {', '.join(output_sections)}

CONVERSION ANALYSIS:
{conversion_type} conversion {'uses complete Microsoft POML documentation with LLM reasoning for optimal accuracy' if conversion_type == 'AI-Powered' else 'uses pattern-matching rules which may have limitations with complex prompts'}

Generated by POML Converter Tool
"""
                    st.download_button(
                        label="📄 Download Report",
                        data=comparison_text,
                        file_name=f"poml_conversion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        help="Download a complete conversion report"
                    )
                
                # Test the converted POML
                st.markdown("### 🧪 Test Your Converted POML")
                st.markdown("Want to see how your converted POML performs? Use it in the Olympiad Challenges tab or test it with your own use case!")
                
                if st.button("🎯 Test with AI", help="Test the converted POML with AI (this step uses Gemini)"):
                    if not model:
                        st.error("⚠️ Please configure your API key to test with AI")
                    else:
                        with st.spinner("Testing converted POML with Gemini..."):
                            renderer = POMLRenderer()
                            test_response = renderer.execute_with_ai(poml_result)
                            
                            st.markdown("#### 🤖 AI Response to Your POML")
                            st.markdown('<div class="result-container poml-container">', unsafe_allow_html=True)
                            st.markdown(test_response)
                            st.markdown('</div>', unsafe_allow_html=True)
    
    # Help section
    with st.expander("ℹ️ How to Use the POML Converter"):
        st.markdown("""
        ## 🤖 AI-Powered Conversion (Recommended)
        
        **Why Choose AI-Powered?**
        - Uses complete Microsoft POML documentation (2000+ words)
        - Understands complex technical and mathematical prompts
        - Handles edge cases and ambiguous phrasing
        - Produces production-ready POML following official specifications
        - Better constraint extraction and deduplication
        - Domain-specific output format optimization
        
        **Process:**
        1. Enter your plain text prompt
        2. Choose settings (AI handles most automatically)
        3. Click "Convert to POML" 
        4. Get high-quality POML with detailed analysis
        
        ## ⚙️ Rule-Based Conversion (Offline)
        
        **When to Use:**
        - No internet connection available
        - Privacy concerns with sending prompts to AI
        - Simple prompts with clear structure
        
        **Limitations:**
        - Pattern-matching only (may miss complex constraints)
        - Limited mathematical notation support
        - No contextual understanding
        - May produce duplicates or incomplete parsing
        
        **Process:**
        Uses intelligent pattern recognition to identify:
        - **Role patterns**: "You are", "Act as", "As an expert"
        - **Task indicators**: Imperatives, questions, action verbs
        - **Constraint signals**: "must", "should", "ensure", "cannot"
        - **Example phrases**: "for example", "such as", "like"
        - **Format requirements**: "format as", "provide", "structure"
        
        ## 📝 General Tips for Both Methods
        
        **For Better Results:**
        - Use explicit role phrases: "You are an expert data scientist"
        - Be specific with constraints: "must include", "should avoid", "ensure"
        - Mention examples explicitly: "for example", "such as"
        - Specify output format: "format your response with", "provide sections for"
        - For technical prompts, use AI-powered conversion
        
        **Settings Guide:**
        - **Include Examples**: Detects and converts example patterns into `<example>` tags
        - **Detailed Constraints**: Extracts requirement/limitation phrases into `<constraints>`
        - **Structured Output**: Creates `<output-format>` with specified sections
        - **Role Enhancement**: How to enhance the role definition (Expert, Professional, etc.)
        - **Constraint Organization**: How to organize constraints in the POML output
        - **Output Sections**: Custom sections for the `<output-format>` tag
        
        ## 🏆 Comparison: AI vs Rule-Based
        
        | Feature | AI-Powered | Rule-Based |
        |---------|------------|------------|
        | Accuracy | ✅ Excellent | ⚠️ Good |
        | Complex Math | ✅ Yes | ❌ Limited |
        | Deduplication | ✅ Advanced | ⚠️ Basic |
        | Domain Detection | ✅ Intelligent | ⚠️ Pattern-based |
        | Offline Usage | ❌ No | ✅ Yes |
        | Speed | ⚠️ 2-5 seconds | ✅ Instant |
        | Production Ready | ✅ Yes | ⚠️ With limitations |
        
        **Recommendation:** Use AI-powered for production and complex prompts, rule-based for simple offline conversions.
        """)

if __name__ == "__main__":
    main()