import streamlit as st
from nutrition import calculate_nutritional_needs
from database import get_nutritional_info
import sqlite3
from fuzzywuzzy import process
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Function to fetch all food names from the database
def get_all_food_names():
    conn = sqlite3.connect('gizi_indo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT NAMA FROM indonesian_food_composition")
    food_names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return food_names

def main():
    st.title('Cek Kebutuhan Gizi')

    # Fetch food names from the database
    food_names = get_all_food_names()

    # Initialize session state for foods list
    if 'foods' not in st.session_state:
        st.session_state.foods = []

    # Custom CSS for button styling
    st.markdown(
        """
        <style>
        div.stButton > button {
            background-color: white;
            color: black;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Columns for input
    col1, col2, col3 = st.columns(3)

    # Input for food items
    with col1:
        st.header('Tambahkan Makanan')
        food_name_input = st.text_input("Masukkan nama makanan:")
        if st.button('Tambahkan') and food_name_input.strip():
            # Use fuzzy matching to find closest match
            best_match, score = process.extractOne(food_name_input, food_names)
            if score >= 60:
                nutrition_info = get_nutritional_info(best_match)
                if nutrition_info:
                    # Convert nutritional values to float
                    nutrition_info = (nutrition_info[0], nutrition_info[1], float(nutrition_info[2]), float(nutrition_info[3]),
                                    float(nutrition_info[4]), float(nutrition_info[5]), float(nutrition_info[6]), float(nutrition_info[7]))
                    st.session_state.foods.append(nutrition_info)
                    st.success("Makanan berhasil ditambahkan.")
                    food_name_input = ""  # Clear input after adding food
                else:
                    st.warning("Makanan tidak ditemukan di database.")
            else:
                st.warning("Makanan tidak ditemukan di database. Pastikan nama makanan benar atau coba yang lain.")

    with col2:
        st.header('Data Pengguna')
        age_group = st.selectbox(
            "Pilih kelompok umur:",
            ["16 - 18 Tahun", "19 - 29 tahun", "30 - 49 tahun"]
        )
        if age_group == "16 - 18 Tahun":
            age_group = 1
        elif age_group == "19 - 29 tahun":
            age_group = 2
        elif age_group == "30 - 49 tahun":
            age_group = 3

    with col3:
        st.header('Trimester Kehamilan')
        trimester = st.selectbox(
            "Pilih trimester kehamilan:",
            ["Trimester 1", "Trimester 2", "Trimester 3"]
        )
        if trimester == "Trimester 1":
            trimester = 1
        elif trimester == "Trimester 2":
            trimester = 2
        elif trimester == "Trimester 3":
            trimester = 3

    # Button to calculate
    if st.button('Hitung'):
        if not st.session_state.foods:
            st.warning("Tidak ada makanan yang ditambahkan. Silakan tambahkan makanan terlebih dahulu.")
            return

        total_nutrition = {
            "Air": sum(food[2] for food in st.session_state.foods),
            "Energi": sum(food[3] for food in st.session_state.foods),
            "Protein": sum(food[4] for food in st.session_state.foods),
            "Lemak": sum(food[5] for food in st.session_state.foods),
            "Karbohidrat": sum(food[6] for food in st.session_state.foods),
            "Serat": sum(food[7] for food in st.session_state.foods)
        }

        age_group_str, trimester_str, needs = calculate_nutritional_needs(age_group, trimester)

        # Display nutritional needs based on input
        st.header('Hasil Kebutuhan Gizi')
        st.subheader('Data Pengguna:')
        st.write(f"Kelompok Umur: {age_group_str}")
        st.write(f"Trimester Kehamilan: {trimester_str}")

        # Display total nutrition from added foods in a table
        st.subheader('Total nilai gizi makanan:')

        # Format the values with 2 decimal places using f-strings and the '{:n.2f}' format specifier
        nutrition_table_formatted = {
            "Nutrien": ["Air", "Energi", "Protein", "Lemak", "Karbohidrat", "Serat"],
            "Total": [f"{total_nutrition['Air']:.2f}", f"{total_nutrition['Energi']:.2f}",
                    f"{total_nutrition['Protein']:.2f}", f"{total_nutrition['Lemak']:.2f}",
                    f"{total_nutrition['Karbohidrat']:.2f}", f"{total_nutrition['Serat']:.2f}"]
        }

        st.table(nutrition_table_formatted)

        # Calculate nutritional deficiencies
        selisih_gizi = {
            "Air": needs["Air"] - total_nutrition["Air"],
            "Energi": needs["Energi"] - total_nutrition["Energi"],
            "Protein": needs["Protein"] - total_nutrition["Protein"],
            "Lemak": needs["Lemak"] - total_nutrition["Lemak"],
            "Karbohidrat": needs["Karbohidrat"] - total_nutrition["Karbohidrat"],
            "Serat": needs["Serat"] - total_nutrition["Serat"]
        }

        # Display nutritional deficiencies in a table
        st.subheader('Kekurangan gizi kamu:')

        # Format the values with 2 decimal places using f-strings and the '{:n.2f}' format specifier
        deficiency_table_formatted = {
            "Nutrien": ["Air", "Energi", "Protein", "Lemak", "Karbohidrat", "Serat"],
            "Selisih": [f"{selisih_gizi['Air']:.2f}", f"{selisih_gizi['Energi']:.2f}",
                    f"{selisih_gizi['Protein']:.2f}", f"{selisih_gizi['Lemak']:.2f}",
                    f"{selisih_gizi['Karbohidrat']:.2f}", f"{selisih_gizi['Serat']:.2f}"]
        }

        st.table(deficiency_table_formatted)

        # Display pie chart for each nutrient
        st.subheader('Perbandingan Total Nilai Gizi dan Selisih Kekurangan Gizi (Pie Chart)')
        nutrients = ["Energi", "Protein", "Lemak", "Karbohidrat", "Serat", "Air"]

        fig, axes = plt.subplots(2, 3, figsize=(5,3), subplot_kw=dict(aspect="equal"))
        fig.patch.set_facecolor((1, 1, 1, 0.7))

        for i, nutrient in enumerate(nutrients):
            row = i // 3
            col = i % 3
            sizes = [max(total_nutrition[nutrient], 0), max(selisih_gizi[nutrient], 0)]
            colors = ['#1f77b4', '#aec7e8']  # Blue shades
            wedges, texts, autotexts = axes[row, col].pie(sizes, autopct='%1.1f%%', startangle=140, colors=colors)
            axes[row, col].set_title(nutrient, fontsize=3, fontweight='bold')

            # Set properties of text
            for autotext in autotexts:
                autotext.set_fontsize(3)
                autotext.set_fontweight('bold')

        plt.legend(['Total Gizi', 'Selisih Gizi'], loc='upper left', fontsize=3)
        plt.tight_layout()
        st.pyplot(fig)

        # Prepare data for bar plot
        nutrition_data = {
            "Nutrien": ["Energi", "Protein", "Lemak", "Karbohidrat", "Serat", "Air"],
            "Total": [total_nutrition["Energi"], total_nutrition["Protein"], total_nutrition["Lemak"],
                      total_nutrition["Karbohidrat"], total_nutrition["Serat"], total_nutrition["Air"]],
            "Selisih": [selisih_gizi["Energi"], selisih_gizi["Protein"], selisih_gizi["Lemak"],
                        selisih_gizi["Karbohidrat"], selisih_gizi["Serat"], selisih_gizi["Air"]]
        }

        # Display bar plot for nutritional data
        st.subheader('Perbandingan Total Nilai Gizi dan Selisih Kekurangan Gizi')
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor((1, 1, 1, 0.7))  # Set background to slightly transparent white

        sns.barplot(x="Nutrien", y="value", hue="variable", data=pd.melt(pd.DataFrame(nutrition_data), ["Nutrien"]), ax=ax, palette=['#1f77b4', '#aec7e8'])
        ax.set_xticklabels(nutrition_data["Nutrien"], fontsize=4, fontweight='bold')
        ax.set_yticklabels(ax.get_yticks(), fontsize=4)
        ax.legend(title="Variabel", fontsize=4, title_fontsize=4)
        ax.set_title("Perbandingan Total Nilai Gizi dan Selisih Kekurangan Gizi per Nutrien", fontsize=6, fontweight='bold')

        ax.set_xlabel('')
        ax.set_ylabel('')

        st.pyplot(fig)

if __name__ == "__main__":
    main()
