
# ==========================================
# Master Flowchart — Study Type Decision Tree
# ==========================================

from graphviz import Digraph


def generate_flowchart(output_path="flowchart.png"):
    dot = Digraph(comment="ClinSample AI Decision Tree")

    dot.attr(rankdir="TB")

    # Root
    dot.node("Start", "What is your primary outcome type?")

    # Main branches
    dot.node("Cont", "Continuous Outcome")
    dot.node("Bin", "Binary Outcome")
    dot.node("Assoc", "Association")
    dot.node("Surv", "Time-to-Event")

    dot.edges([
        ("Start", "Cont"),
        ("Start", "Bin"),
        ("Start", "Assoc"),
        ("Start", "Surv"),
    ])

    # Continuous
    dot.node("C1", "One-Sample Mean")
    dot.node("C2", "Two Independent Means")
    dot.node("C3", "Paired Mean")
    dot.node("C4", "One-Way ANOVA")

    dot.edges([
        ("Cont", "C1"),
        ("Cont", "C2"),
        ("Cont", "C3"),
        ("Cont", "C4"),
    ])

    # Binary
    dot.node("B1", "One Proportion")
    dot.node("B2", "Two Proportions")
    dot.node("B3", "Case-Control (OR)")
    dot.node("B4", "Cohort / Risk Ratio")

    dot.edges([
        ("Bin", "B1"),
        ("Bin", "B2"),
        ("Bin", "B3"),
        ("Bin", "B4"),
    ])

    # Association
    dot.node("A1", "Correlation")
    dot.node("A2", "Linear Regression")
    dot.node("A3", "Logistic Regression (EPV)")

    dot.edges([
        ("Assoc", "A1"),
        ("Assoc", "A2"),
        ("Assoc", "A3"),
    ])

    # Survival
    dot.node("S1", "Log-Rank Test")

    dot.edge("Surv", "S1")

    dot.render(output_path, format="png", cleanup=True)

    return output_path
