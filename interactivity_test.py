import matplotlib.pyplot as plt
import mplcursors

# Sample data
x = [1, 2, 3, 4, 5]
y = [2, 3, 5, 7, 11]

# Create a line plot
plt.plot(x, y, marker='o', linestyle='-')

# Add hover annotations using mplcursors
mplcursors.cursor(hover=True)

# Set labels and title
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Hover Interactivity with mplcursors')

# Show the plot
plt.show()
