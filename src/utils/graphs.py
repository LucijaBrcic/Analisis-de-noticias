import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd

class DataVisualizer:
    
    def __init__(self, df):

        self.df = df

    def create_scatter_plot(self, variable1, variable2, hue=None):

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
 
        # Select only numeric columns
        numeric_df = self.df.select_dtypes(include=["number"])

        # Compute correlation matrix
        corr_matrix = numeric_df.corr()

        # Convert to numpy array for plotting
        z = corr_matrix.values

        # Column and row labels
        x_labels = corr_matrix.columns.tolist()
        y_labels = corr_matrix.index.tolist()

        # Create heatmap
        fig = ff.create_annotated_heatmap(
            z=z, x=x_labels, y=y_labels,
            colorscale="Viridis",  # Choose color scheme
            showscale=True  # Show color bar
        )

        # Update layout
        fig.update_layout(title=title, height=500)

        return fig
