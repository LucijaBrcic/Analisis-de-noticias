import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd

class DataVisualizer:
    
    def __init__(self, df):
        """
        Initialize the DataVisualizer class with a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
        """
        self.df = df

    def create_scatter_plot(self, variable1, variable2, hue=None):
        """
        Creates a scatter plot using Plotly.

        Args:
            variable1 (str): The first numeric variable for the x-axis.
            variable2 (str): The second numeric variable for the y-axis.
            hue (str, optional): The column to color points by. Defaults to None.

        Returns:
            plotly.graph_objects.Figure: The scatter plot.
        """
        color_param = hue if hue and hue != "None" else None

        fig = px.scatter(
            self.df, x=variable1, y=variable2,
            color=color_param,
            title=f'{variable1} vs {variable2}', 
            log_x=True, log_y=True,
            render_mode="webgl"
        )

        return fig

    def create_heatmap(self, title="Correlation Heatmap"):
        """
        Creates a correlation heatmap using Plotly.

        Args:
            title (str, optional): The title of the heatmap. Defaults to "Correlation Heatmap".

        Returns:
            plotly.graph_objects.Figure: The correlation heatmap.
        """
        # Select only numeric columns
        numeric_df = self.df.select_dtypes(include=["number"])

        # Compute correlation matrix
        corr_matrix = numeric_df.corr().round(2)  # Round values to 2 decimal places

        # Convert to numpy array for plotting
        z = corr_matrix.values

        # Column and row labels
        x_labels = corr_matrix.columns.tolist()
        y_labels = corr_matrix.index.tolist()

        # Create heatmap
        fig = ff.create_annotated_heatmap(
            z=z, x=x_labels, y=y_labels,
            annotation_text=corr_matrix.round(2).values,  # Display rounded values
            colorscale="Viridis",  # Choose color scheme
            showscale=True  # Show color bar
        )

        # Update layout with increased height
        fig.update_layout(title=title, height=700)  # Increased height for better visualization

        return fig

    def count_plot(self, column):
        """
        Creates a bar chart showing the percentage of the top 15 most common instances in a categorical column,
        excluding "Desconocido".

        Args:
            column (str): The categorical column to analyze.

        Returns:
            plotly.graph_objects.Figure: The bar chart figure.
        """
        # Remove "Desconocido" if it exists
        filtered_df = self.df[self.df[column] != "Desconocido"]

        # Count occurrences and compute percentages
        category_counts = filtered_df[column].value_counts(normalize=True).nlargest(15).reset_index()
        category_counts.columns = [column, "percentage"]
        category_counts["percentage"] *= 100  # Convert to percentage

        # Create bar plot
        fig = px.bar(
            category_counts, 
            x=column, 
            y="percentage",
            text=category_counts["percentage"].apply(lambda x: f"{x:.2f}%"),  # Show percentage on bars
            title=f"Distribución de noticias por {column} (Top 15, %)",
            color=column,  # Color by category
            color_discrete_sequence=px.colors.qualitative.Set2  # Choose color palette
        )

        # Update layout for better readability
        fig.update_layout(
            xaxis_title=column.capitalize(),
            yaxis_title="Porcentaje de noticias",
            title_font_size=18,
            xaxis_tickangle=-45,  # Rotate labels if needed
            height=500,  # Adjust height
        )

        return fig


    def create_boxplot(self, variable):
        """
        Creates a boxplot showing the distribution of a continuous variable across different categories,
        ordered by mean from highest to lowest.

        Args:
            variable (str): The continuous variable to visualize.

        Returns:
            plotly.graph_objects.Figure: The boxplot figure.
        """
        # Ensure 'category' and the selected variable exist in the DataFrame
        if "category" not in self.df.columns:
            raise KeyError("The column 'category' is missing in the DataFrame.")
        if variable not in self.df.columns:
            raise KeyError(f"The variable '{variable}' is missing in the DataFrame.")

        # Compute mean for each category and sort by mean (descending)
        category_means = self.df.groupby("category")[variable].mean().sort_values(ascending=False).index.tolist()

        # Create the boxplot with ordered categories
        fig = px.box(
            self.df, 
            x="category", 
            y=variable,
            title=f"Distribución de {variable} por categoría (Ordenado por Media)",
            category_orders={"category": category_means},  # Order by computed means
            color="category",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )

        # Improve layout
        fig.update_layout(
            xaxis_title="Categoría",
            yaxis_title=f"Distribución de {variable}",
            xaxis_tickangle=-45,  # Rotate labels for better readability
            height=600
        )

        return fig

