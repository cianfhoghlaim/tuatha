"""tuatha.notebooks.media_intel — the marimo notebook for the 5-class media descriptor pipeline.
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
        # Media Intel Marimo Notebook

        The the 5-class media descriptor pipeline.
        """
    )
    return (mo,)


if __name__ == "__main__":
    app.run()
