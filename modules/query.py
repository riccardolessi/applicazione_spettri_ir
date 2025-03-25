from shiny import module, reactive, render, ui
from htmltools import HTML, div

@module.ui
def query_output_ui():
    return (
        ui.card(
            ui.input_text_area(
                "sql_query",
                "",
                value="",
                width="100%",
                height="200px",
            ),
            ui.layout_columns(
                ui.input_action_button("run", "Run", class_="btn btn-primary"),
            ),
            ui.output_data_frame("results"),
            ui.output_ui("struttura_db")
        ),
    )


@module.server
def query_output_server(input, output, session, db):

    @render.data_frame
    @reactive.event(input.run)
    def results():
        qry = input.sql_query().replace("\n", " ")

        result = db.query(qry)
        
        return result
    
    @render.ui
    def struttura_db():
        struttura = db.tabelle()

        return div(HTML(struttura))