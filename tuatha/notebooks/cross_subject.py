"""tuatha.notebooks.cross_subject — the marimo notebook for cross-medium consistency score.
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
        # Cross Subject Marimo Notebook

        The cross-medium consistency score.
        """
    )
    return (mo,)


if __name__ == "__main__":
    app.run()
