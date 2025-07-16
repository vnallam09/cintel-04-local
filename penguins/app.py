"""
Teja's Penguin Data Dashboard
"""
import seaborn as sns
import matplotlib.pyplot as plt
from palmerpenguins import load_penguins
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget

# Import plotly differently for Pyodide compatibility
from plotly import graph_objects as go
import plotly.express as px

# Use the built-in function to load the Palmer Penguins dataset
penguins_df = load_penguins().dropna(axis=0)

app_ui =  ui.page_fluid(
    ui.page_sidebar(
        ui.sidebar(
            ui.h2("Sidebar"),
            ui.input_selectize(
                "selected_attribute",
                "Select Attribute",
                ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
            ),
            ui.input_numeric(                
                "plotly_bin_count",
                "Number of Plotly Histogram Bins",
                10
            ),
            ui.input_slider(
                'seaborn_bin_count',
                "Number of Seaborn Histogram Bins",
                5, 
                50,
                10
            ),
            ui.input_checkbox_group(
                "selected_species",
                "Select Species",
                ["Adelie", "Chinstrap", "Gentoo"],
                selected=["Adelie", "Chinstrap", "Gentoo"],
                inline=True
            ), 
            ui.hr(),
            ui.a(
                'Github', 
                href='https://github.com/vnallam09',
                target= "_blank"
            )            
        ),
        ui.layout_columns(
            ui.h2('Data Frame (Full)'),
            ui.h3('Data Grid (Filtered by species)')
        ),
        ui.layout_columns(       
            ui.output_data_frame("data_table"),
            ui.output_data_frame("data_grid")
        ),
        ui.layout_columns(
            output_widget("plotly_histogram"),
            ui.output_plot("seaborn_histogram")
        ),
        ui.card(
            ui.card_header('Plotly Scatter Plot'),
            output_widget("plotly_scatterplot"),
            full_screen=True
        ),
        title="🐧 Teja's Penguin Data Dashboard"
    )
)

def server(input, output, session):
    @render.data_frame
    def data_table():
        return filtered_data()

    # @render_widget
    @render.data_frame
    def data_grid():
        df = filtered_data()
        return df #DataGrid(df)

    @render_widget
    def plotly_histogram():
        df = filtered_data()
        bins = input.plotly_bin_count()
        fig = go.Figure()
        for species in df['species'].unique():
            species_data = df[df['species'] == species]
            fig.add_trace(go.Histogram(
                x=species_data[input.selected_attribute()],
                name=species,
                nbinsx=bins
            ))
        fig.update_layout(title='Plotly Histogram', barmode='overlay')
        return fig

    @output
    @render.plot
    def seaborn_histogram():
        bins = input.seaborn_bin_count()
        ax = sns.histplot(data=filtered_data(), x=f'{input.selected_attribute()}', bins = int(f'{bins}'),  kde = True, hue='species')
        ax.set_title('Seaborn Histogram')
        return ax

    @render_widget
    def plotly_scatterplot():
        df = filtered_data()
        fig = go.Figure()
        for species in df['species'].unique():
            species_data = df[df['species'] == species]
            fig.add_trace(go.Scatter(
                x=species_data['bill_length_mm'],
                y=species_data['bill_depth_mm'],
                mode='markers',
                name=species,
                hovertext=species_data['species']
            ))
        fig.update_layout(
            title="Scatter Plot",
            xaxis_title="Bill Length (mm)",
            yaxis_title="Bill Depth (mm)"
        )
        return fig

    @reactive.calc
    def filtered_data():
        return penguins_df[penguins_df['species'].isin(input.selected_species())]

app = App(app_ui, server)

if __name__ == "__main__":   
    app.run()
