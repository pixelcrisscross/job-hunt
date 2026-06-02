import matplotlib.pyplot as plt

# Set simple, professional style parameters
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']

# Mock data based on the 20 job requirements mentioned in your report
skills = ['SQL', 'Python', 'Data Visualization', 'Machine Learning', 'Flask', 'PostgreSQL', 'HTML/CSS', 'JavaScript']
demand_counts = [18, 15, 12, 10, 8, 7, 5, 4] 

plt.figure(figsize=(10, 5.5))
bars = plt.barh(skills[::-1], demand_counts[::-1], color='#3498db', edgecolor='#2980b9', height=0.6)

# Titles & Labels
plt.title('Skill Demand Distribution (Top Demanded Skills)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Number of Job Requirements Demanding the Skill', fontsize=11, labelpad=10)
plt.ylabel('Skills', fontsize=11, labelpad=10)

# Add accurate label values on the bars
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.3, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
             va='center', ha='left', fontsize=10, fontweight='bold', color='#2c3e50')

plt.xlim(0, max(demand_counts) + 2)
plt.tight_layout()
plt.savefig('skill_demand_chart.png', dpi=300)
print("Saved skill_demand_chart.png successfully!")