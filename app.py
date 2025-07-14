"""
Teja's Penguin Data Dashboard
"""
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from palmerpenguins import load_penguins
from shiny import App, ui, render, reactive
from shinywidgets import render_plotly, output_widget, render_widget
from ipydatagrid import DataGrid

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
            output_widget("data_grid")
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

    @render_widget
    def data_grid():
        df = filtered_data()
        return DataGrid(df)

    @render_widget
    def plotly_histogram():
        bins = input.plotly_bin_count()
        return px.histogram(data_frame=filtered_data(), x=f'{input.selected_attribute()}', nbins=bins, color='species', title='Plotly Histogram')

    @output
    @render.plot
    def seaborn_histogram():
        bins = input.seaborn_bin_count()
        ax = sns.histplot(data=filtered_data(), x=f'{input.selected_attribute()}', bins = int(f'{bins}'),  kde = True, hue='species')
        ax.set_title('Seaborn Histogram')
        return ax

    @render_widget
    def plotly_scatterplot():
        return px.scatter(data_frame=filtered_data(), x='bill_length_mm', y='bill_depth_mm', color='species', hover_name='species', size_max=10, title="Scatter Plot")

    @reactive.calc
    def filtered_data():
        return penguins_df[penguins_df['species'].isin(input.selected_species())]

app = App(app_ui, server)

if __name__ == "__main__":   
    app.run()
