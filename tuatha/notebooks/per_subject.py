"""tuatha.notebooks.per_subject — the marimo notebook for per-medium coverage table.
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
        # Per Subject Marimo Notebook

        The per-medium coverage table.
        """
    )
    return (mo,)


if __name__ == "__main__":
    app.run()
