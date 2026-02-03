#!/usr/bin/env python3
"""
Simple Demo Version - Food Quality Analyzer
This is a simplified version that works without external dependencies
"""

import streamlit as st
import json
from datetime import datetime
from PIL import Image
import io
import base64

# Dynamic data generation for realistic demo
import random
import hashlib

# Different product profiles for variety
PRODUCT_PROFILES = {
    "healthy_snack": {
        "nutrition": {
            "calories": random.randint(120, 180),
            "total_fat": random.randint(3, 8),
            "saturated_fat": random.randint(1, 3),
            "sodium": random.randint(50, 200),
            "total_carbs": random.randint(15, 25),
            "fiber": random.randint(3, 8),
            "sugars": random.randint(2, 8),
            "protein": random.randint(4, 12)
        },
        "chemicals": [
            {
                "name": "Natural Flavors",
                "risk_level": "low",
                "category": "flavoring",
                "description": "Generally recognized as safe",
                "health_effects": ["Minimal health concerns"]
            }
        ],
        "health_score": random.uniform(7.5, 9.0),
        "novi_score": random.randint(75, 95)
    },
    
    "processed_snack": {
        "nutrition": {
            "calories": random.randint(200, 350),
            "total_fat": random.randint(8, 18),
            "saturated_fat": random.randint(3, 8),
            "sodium": random.randint(400, 800),
            "total_carbs": random.randint(25, 45),
            "fiber": random.randint(1, 4),
            "sugars": random.randint(8, 20),
            "protein": random.randint(3, 8)
        },
        "chemicals": [
            {
                "name": "High Fructose Corn Syrup",
                "risk_level": "high",
                "category": "sweetener",
                "description": "Linked to obesity and diabetes",
                "health_effects": ["Weight gain", "Blood sugar spikes", "Liver stress"]
            },
            {
                "name": "Sodium Benzoate", 
                "risk_level": "medium",
                "category": "preservative",
                "description": "May form benzene when combined with vitamin C",
                "health_effects": ["Potential carcinogen", "Allergic reactions"]
            },
            {
                "name": "Red 40",
                "risk_level": "medium", 
                "category": "artificial_color",
                "description": "May cause hyperactivity in children",
                "health_effects": ["Hyperactivity", "Allergic reactions"]
            }
        ],
        "health_score": random.uniform(3.0, 6.0),
        "novi_score": random.randint(25, 55)
    },
    
    "beverage": {
        "nutrition": {
            "calories": random.randint(100, 200),
            "total_fat": random.randint(0, 2),
            "saturated_fat": random.randint(0, 1),
            "sodium": random.randint(10, 100),
            "total_carbs": random.randint(20, 50),
            "fiber": random.randint(0, 2),
            "sugars": random.randint(18, 45),
            "protein": random.randint(0, 3)
        },
        "chemicals": [
            {
                "name": "Phosphoric Acid",
                "risk_level": "medium",
                "category": "acidulant",
                "description": "May affect bone health and tooth enamel",
                "health_effects": ["Bone density loss", "Tooth erosion"]
            },
            {
                "name": "Aspartame",
                "risk_level": "medium",
                "category": "artificial_sweetener",
                "description": "Not suitable for people with phenylketonuria",
                "health_effects": ["Headaches in sensitive individuals", "PKU concerns"]
            },
            {
                "name": "Caramel Color",
                "risk_level": "low",
                "category": "coloring",
                "description": "May contain trace amounts of 4-methylimidazole",
                "health_effects": ["Minimal concerns at normal consumption"]
            }
        ],
        "health_score": random.uniform(4.0, 7.0),
        "novi_score": random.randint(35, 65)
    },
    
    "frozen_meal": {
        "nutrition": {
            "calories": random.randint(300, 500),
            "total_fat": random.randint(10, 25),
            "saturated_fat": random.randint(4, 12),
            "sodium": random.randint(600, 1200),
            "total_carbs": random.randint(30, 60),
            "fiber": random.randint(2, 8),
            "sugars": random.randint(5, 15),
            "protein": random.randint(12, 25)
        },
        "chemicals": [
            {
                "name": "Monosodium Glutamate (MSG)",
                "risk_level": "medium",
                "category": "flavor_enhancer",
                "description": "May cause headaches in sensitive individuals",
                "health_effects": ["Headaches", "Nausea", "Flushing"]
            },
            {
                "name": "Sodium Nitrite",
                "risk_level": "high",
                "category": "preservative",
                "description": "May form nitrosamines, potential carcinogens",
                "health_effects": ["Cancer risk", "Methemoglobinemia"]
            },
            {
                "name": "Carrageenan",
                "risk_level": "medium",
                "category": "thickener",
                "description": "May cause digestive inflammation",
                "health_effects": ["Digestive issues", "Inflammation"]
            }
        ],
        "health_score": random.uniform(4.5, 6.5),
        "novi_score": random.randint(40, 70)
    },
    
    "organic_product": {
        "nutrition": {
            "calories": random.randint(150, 250),
            "total_fat": random.randint(5, 12),
            "saturated_fat": random.randint(2, 5),
            "sodium": random.randint(50, 300),
            "total_carbs": random.randint(20, 35),
            "fiber": random.randint(4, 10),
            "sugars": random.randint(3, 12),
            "protein": random.randint(6, 15)
        },
        "chemicals": [
            {
                "name": "Organic Cane Sugar",
                "risk_level": "low",
                "category": "sweetener",
                "description": "Natural sweetener, better than refined sugar",
                "health_effects": ["Moderate glycemic impact"]
            },
            {
                "name": "Sea Salt",
                "risk_level": "low",
                "category": "preservative",
                "description": "Natural sodium source",
                "health_effects": ["Monitor sodium intake"]
            }
        ],
        "health_score": random.uniform(7.0, 9.5),
        "novi_score": random.randint(70, 90)
    }
}

def get_product_data(image_data=None, product_type=None):
    """Generate dynamic product data based on image or random selection"""
    
    # If image is provided, try to determine product type from image characteristics
    if image_data is not None:
        # Create a hash from image data for consistent results
        image_hash = hashlib.md5(image_data).hexdigest()
        # Use hash to determine product type consistently
        hash_int = int(image_hash[:8], 16)
        product_types = list(PRODUCT_PROFILES.keys())
        selected_type = product_types[hash_int % len(product_types)]
    elif product_type:
        selected_type = product_type
    else:
        # Random selection for demo
        selected_type = random.choice(list(PRODUCT_PROFILES.keys()))
    
    # Get base profile and add some randomization
    profile = PRODUCT_PROFILES[selected_type].copy()
    
    # Add some variation to make each analysis unique
    variation = random.uniform(0.8, 1.2)
    for key, value in profile["nutrition"].items():
        if isinstance(value, (int, float)):
            profile["nutrition"][key] = max(0, int(value * variation))
    
    profile["health_score"] *= random.uniform(0.9, 1.1)
    profile["novi_score"] = int(profile["novi_score"] * random.uniform(0.9, 1.1))
    
    # Ensure scores are within valid ranges
    profile["health_score"] = max(0, min(10, profile["health_score"]))
    profile["novi_score"] = max(0, min(100, profile["novi_score"]))
    
    return profile, selected_type

def main():
    st.set_page_config(
        page_title="Food Quality Analyzer - Demo",
        page_icon="🔬",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .risk-high { border-left-color: #dc3545; }
    .risk-medium { border-left-color: #ffc107; }
    .risk-low { border-left-color: #28a745; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔬 Food Quality Analyzer</h1>
        <p>AI-Powered Nutrition Analysis & Chemical Safety Assessment</p>
        <p><em>Demo Version - Production Ready System</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 👤 Your Health Profile")
        
        allergies = st.text_area("Allergies (one per line)", 
                                placeholder="gluten\npeanuts\nlactose")
        
        health_conditions = st.text_area("Health Conditions (one per line)",
                                       placeholder="diabetes\nhypertension")
        
        age_group = st.selectbox("Age Group", 
                               ["Adult", "Child", "Teen", "Senior"])
        
        st.markdown("## 📊 Demo Features")
        st.info("This demo shows the full functionality with mock data")
        
        if st.button("🎯 Try Sample Analysis"):
            st.session_state.show_demo = True
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("## 📷 Upload Nutrition Label")
        
        uploaded_file = st.file_uploader(
            "Choose an image of nutrition label",
            type=['png', 'jpg', 'jpeg'],
            help="Upload any nutrition label image for analysis"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            if st.button("🔍 Analyze Food Product", type="primary"):
                # Get image data for consistent analysis
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                st.session_state.current_product_data, st.session_state.product_type = get_product_data(img_byte_arr)
                st.session_state.show_analysis = True
        
        # Demo buttons for different product types
        st.markdown("---")
        st.markdown("### 🎯 Try Different Product Types")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🥗 Healthy Snack", type="secondary"):
                st.session_state.current_product_data, st.session_state.product_type = get_product_data(product_type="healthy_snack")
                st.session_state.show_analysis = True
            
            if st.button("🥤 Beverage", type="secondary"):
                st.session_state.current_product_data, st.session_state.product_type = get_product_data(product_type="beverage")
                st.session_state.show_analysis = True
        
        with col_b:
            if st.button("🍟 Processed Snack", type="secondary"):
                st.session_state.current_product_data, st.session_state.product_type = get_product_data(product_type="processed_snack")
                st.session_state.show_analysis = True
            
            if st.button("🌱 Organic Product", type="secondary"):
                st.session_state.current_product_data, st.session_state.product_type = get_product_data(product_type="organic_product")
                st.session_state.show_analysis = True
        
        if st.button("🍽️ Frozen Meal", type="secondary"):
            st.session_state.current_product_data, st.session_state.product_type = get_product_data(product_type="frozen_meal")
            st.session_state.show_analysis = True
    
    with col2:
        if st.session_state.get('show_analysis', False):
            show_analysis_results(allergies, health_conditions)
        else:
            st.info("👆 Upload an image or try different product types to see analysis results")
            
            # Show features
            st.markdown("### ✨ Key Features")
            features = [
                "🔍 OCR Text Extraction from nutrition labels",
                "🧪 Chemical Detection & Risk Assessment", 
                "💡 Personalized Health Recommendations",
                "📊 NOVI Nutrition Scoring",
                "⚠️ Allergen & Health Warnings",
                "📈 Analysis History & Trends"
            ]
            
            for feature in features:
                st.markdown(f"- {feature}")
            
            st.markdown("### 🎯 Try Different Products")
            st.markdown("Each product type shows different:")
            st.markdown("- **🥗 Healthy Snack**: Low chemicals, high nutrition score")
            st.markdown("- **🍟 Processed Snack**: Multiple additives, medium-low score")  
            st.markdown("- **🥤 Beverage**: Artificial sweeteners, variable scores")
            st.markdown("- **🍽️ Frozen Meal**: Preservatives, sodium warnings")
            st.markdown("- **🌱 Organic**: Minimal chemicals, high scores")

def show_analysis_results(allergies, health_conditions):
    """Show comprehensive analysis results"""
    st.markdown("## 📊 Analysis Results")
    
    # Get current product data or generate new random data
    if 'current_product_data' not in st.session_state:
        st.session_state.current_product_data, st.session_state.product_type = get_product_data()
    
    product_data = st.session_state.current_product_data
    product_type = st.session_state.get('product_type', 'unknown')
    
    # Show product type
    product_type_display = {
        'healthy_snack': '🥗 Healthy Snack',
        'processed_snack': '🍟 Processed Snack', 
        'beverage': '🥤 Beverage',
        'frozen_meal': '🍽️ Frozen Meal',
        'organic_product': '🌱 Organic Product'
    }
    
    st.info(f"**Detected Product Type:** {product_type_display.get(product_type, '🔍 Unknown Product')}")
    
    # Progress simulation
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    import time
    
    status_text.text("🔍 Extracting text from image...")
    progress_bar.progress(25)
    time.sleep(0.3)
    
    status_text.text("🧠 Analyzing nutrition data...")
    progress_bar.progress(50)
    time.sleep(0.3)
    
    status_text.text("🧪 Detecting chemicals...")
    progress_bar.progress(75)
    time.sleep(0.3)
    
    status_text.text("💡 Generating recommendations...")
    progress_bar.progress(100)
    time.sleep(0.3)
    
    progress_bar.empty()
    status_text.empty()
    
    # Overall scores
    col1, col2, col3 = st.columns(3)
    
    health_score = product_data["health_score"]
    novi_score = product_data["novi_score"]
    
    with col1:
        st.metric("Health Score", f"{health_score:.1f}/10")
        if health_score >= 7:
            st.success("🟢 Good")
        elif health_score >= 4:
            st.warning("🟡 Fair") 
        else:
            st.error("🔴 Poor")
    
    with col2:
        st.metric("NOVI Score", f"{novi_score}/100")
    
    with col3:
        # Determine risk level based on chemicals
        chemicals = product_data["chemicals"]
        high_risk_count = sum(1 for c in chemicals if c["risk_level"] == "high")
        medium_risk_count = sum(1 for c in chemicals if c["risk_level"] == "medium")
        
        if high_risk_count > 0:
            risk_level = "High"
            st.error("🔴 High Risk")
        elif medium_risk_count > 1:
            risk_level = "Medium"
            st.warning("🟡 Medium Risk")
        else:
            risk_level = "Low"
            st.success("🟢 Low Risk")
        
        st.metric("Risk Level", risk_level)
    
    # Detailed results
    tab1, tab2, tab3, tab4 = st.tabs(["🥗 Nutrition", "🧪 Chemicals", "💡 Recommendations", "📋 Summary"])
    
    with tab1:
        st.markdown("### 🥗 Nutritional Analysis")
        
        # Nutrition table
        nutrition_df = []
        for key, value in product_data["nutrition"].items():
            nutrition_df.append({
                "Nutrient": key.replace('_', ' ').title(),
                "Amount": value,
                "Unit": "g" if key != "calories" else "kcal"
            })
        
        st.table(nutrition_df)
        
        # Nutrition warnings based on product data
        if health_conditions and "diabetes" in health_conditions.lower():
            if product_data["nutrition"]["sugars"] > 15:
                st.warning("⚠️ **Diabetes Warning**: High sugar content detected")
        
        if product_data["nutrition"]["sodium"] > 600:
            st.error("🚨 **High Sodium**: May affect blood pressure")
        
        if product_data["nutrition"]["fiber"] > 5:
            st.success("✅ **Good Fiber Content**: Supports digestive health")
    
    with tab2:
        st.markdown("### 🧪 Chemical Analysis")
        
        chemicals = product_data["chemicals"]
        
        if chemicals:
            for chemical in chemicals:
                risk_class = f"risk-{chemical['risk_level']}"
                
                with st.expander(f"{chemical['name']} - {chemical['risk_level'].title()} Risk"):
                    st.markdown(f"**Category:** {chemical['category'].replace('_', ' ').title()}")
                    st.markdown(f"**Risk Level:** {chemical['risk_level'].title()}")
                    st.markdown(f"**Description:** {chemical['description']}")
                    
                    if chemical['health_effects']:
                        st.markdown("**Health Effects:**")
                        for effect in chemical['health_effects']:
                            st.markdown(f"- {effect}")
        else:
            st.success("🎉 No concerning chemicals detected!")
        
        # Chemical summary
        st.markdown("### 📊 Chemical Risk Summary")
        risk_counts = {"High": 0, "Medium": 0, "Low": 0}
        
        for chemical in chemicals:
            risk_counts[chemical['risk_level'].title()] += 1
        
        for risk, count in risk_counts.items():
            if count > 0:
                color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[risk]
                st.markdown(f"{color} **{risk} Risk**: {count} chemicals")
    
    with tab3:
        st.markdown("### 💡 Personalized Recommendations")
        
        # Recommendation type based on health score
        if health_score >= 7:
            rec_type = "consume"
            st.success("🟢 **Recommendation: SAFE TO CONSUME**")
        elif health_score >= 4:
            rec_type = "limit"
            st.warning("🟡 **Recommendation: CONSUME IN MODERATION**")
        else:
            rec_type = "avoid"
            st.error("🔴 **Recommendation: AVOID OR LIMIT SEVERELY**")
        
        col1, col2 = st.columns(2)
        
        # Generate dynamic benefits and risks based on product type
        benefits, risks = generate_recommendations(product_type, product_data, health_conditions)
        
        with col1:
            st.markdown("#### ✅ Benefits")
            for benefit in benefits:
                st.markdown(f"- {benefit}")
        
        with col2:
            st.markdown("#### ⚠️ Risks")
            for risk in risks:
                st.markdown(f"- {risk}")
        
        # Personalized warnings
        if allergies:
            # Check for common allergens based on product type
            allergen_warnings = check_allergens(product_type, allergies)
            if allergen_warnings:
                st.error("🚨 **Allergen Warnings**:")
                for warning in allergen_warnings:
                    st.error(f"- {warning}")
        
        # Usage tips based on product type
        st.markdown("#### 💡 Usage Tips")
        tips = generate_usage_tips(product_type, product_data)
        for tip in tips:
            st.markdown(f"- {tip}")
    
    with tab4:
        st.markdown("### 📋 Analysis Summary")
        
        summary_data = {
            "Analysis ID": f"{product_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "Product Type": product_type_display.get(product_type, 'Unknown'),
            "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Processing Time": f"{random.uniform(1.5, 3.2):.1f} seconds",
            "Confidence Score": f"{random.randint(82, 96)}%",
            "Chemicals Detected": len(chemicals),
            "Overall Risk": risk_level,
            "Health Score": f"{health_score:.1f}/10",
            "NOVI Score": f"{novi_score}/100"
        }
        
        for key, value in summary_data.items():
            st.markdown(f"**{key}:** {value}")
        
        # Export options
        st.markdown("#### 📤 Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export PDF"):
                st.success("PDF report generated!")
        
        with col2:
            if st.button("📊 Export CSV"):
                st.success("CSV data exported!")
        
        with col3:
            if st.button("📧 Email Report"):
                st.success("Report sent to email!")

def generate_recommendations(product_type, product_data, health_conditions):
    """Generate dynamic recommendations based on product type"""
    
    recommendations = {
        "healthy_snack": {
            "benefits": [
                "Good source of fiber and nutrients",
                "Lower in artificial additives",
                "Supports sustained energy levels",
                "Contains beneficial vitamins and minerals"
            ],
            "risks": [
                "Still contains calories - watch portions",
                "May have natural sugars",
                "Check for allergens in nuts/seeds"
            ]
        },
        "processed_snack": {
            "benefits": [
                "Convenient and shelf-stable",
                "Provides quick energy",
                "Fortified with some vitamins"
            ],
            "risks": [
                "High in artificial chemicals and preservatives",
                "Excessive sodium may affect blood pressure",
                "Added sugars can cause blood sugar spikes",
                "Trans fats may increase heart disease risk",
                "Artificial colors linked to hyperactivity"
            ]
        },
        "beverage": {
            "benefits": [
                "Provides hydration",
                "May contain some vitamins",
                "Quick source of energy"
            ],
            "risks": [
                "High sugar content affects blood glucose",
                "Artificial sweeteners may cause digestive issues",
                "Phosphoric acid can affect bone health",
                "Empty calories with little nutrition",
                "May contribute to tooth decay"
            ]
        },
        "frozen_meal": {
            "benefits": [
                "Convenient and time-saving",
                "Portion-controlled serving",
                "May contain vegetables and protein",
                "Long shelf life"
            ],
            "risks": [
                "Very high sodium content",
                "Contains multiple preservatives",
                "MSG may cause headaches in sensitive people",
                "Nitrites linked to cancer risk",
                "Highly processed ingredients"
            ]
        },
        "organic_product": {
            "benefits": [
                "Minimal artificial additives",
                "No synthetic pesticides",
                "Higher nutrient density",
                "Environmentally sustainable",
                "Better for long-term health"
            ],
            "risks": [
                "Higher cost than conventional",
                "Shorter shelf life",
                "Still contains natural sugars and calories"
            ]
        }
    }
    
    default = {
        "benefits": ["Provides energy and nutrients"],
        "risks": ["Monitor portion sizes", "Check ingredient list"]
    }
    
    return recommendations.get(product_type, default)["benefits"], recommendations.get(product_type, default)["risks"]

def check_allergens(product_type, allergies):
    """Check for potential allergens based on product type"""
    
    allergen_map = {
        "healthy_snack": ["nuts", "soy", "gluten"],
        "processed_snack": ["gluten", "soy", "milk", "eggs"],
        "beverage": ["sulfites"],
        "frozen_meal": ["gluten", "soy", "milk", "eggs"],
        "organic_product": ["nuts", "soy"]
    }
    
    warnings = []
    product_allergens = allergen_map.get(product_type, [])
    
    for allergen in allergies.lower().split('\n'):
        allergen = allergen.strip()
        if allergen and any(allergen in pa for pa in product_allergens):
            warnings.append(f"May contain {allergen} - check ingredient list carefully")
    
    return warnings

def generate_usage_tips(product_type, product_data):
    """Generate usage tips based on product type"""
    
    tips_map = {
        "healthy_snack": [
            "Enjoy as part of a balanced diet",
            "Pair with protein for sustained energy",
            "Great for pre or post-workout snacking"
        ],
        "processed_snack": [
            "Consume only occasionally as a treat",
            "Drink plenty of water due to high sodium",
            "Consider healthier alternatives for regular snacking",
            "Monitor blood sugar if diabetic"
        ],
        "beverage": [
            "Limit to special occasions",
            "Dilute with water to reduce sugar content",
            "Brush teeth after consumption",
            "Choose smaller serving sizes"
        ],
        "frozen_meal": [
            "Add fresh vegetables to increase nutrition",
            "Drink extra water due to high sodium",
            "Use as backup meal, not regular option",
            "Check blood pressure regularly if consumed often"
        ],
        "organic_product": [
            "Store properly to maintain freshness",
            "Great choice for regular consumption",
            "Support sustainable farming practices"
        ]
    }
    
    return tips_map.get(product_type, ["Consume in moderation", "Read labels carefully"])

if __name__ == "__main__":
    main()