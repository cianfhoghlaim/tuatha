"""tuatha.notebooks.hackathon — the marimo notebook for the 4 BIEP hackathon features.
"""
import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        f"""
        # Hackathon Marimo Notebook

        The the 4 BIEP hackathon features.
        """
    )
    return (mo,)


if __name__ == "__main__":
    app.run()
