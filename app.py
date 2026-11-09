"""Дашборд пассажиропотока. Вариант 00 — резервный набор данных."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html


DATA_PATH = Path(__file__).resolve().with_name("data.csv")

# TODO 1. Читаем CSV; даты сразу преобразуются в datetime.
df = pd.read_csv(DATA_PATH, parse_dates=["date"])

# TODO 2. Получаем отсортированный список маршрутов.
route_names = sorted(df["route"].unique())


def empty_figure(message):
    """Готовая заглушка: менять эту функцию не требуется."""
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    figure.update_layout(template="plotly_white", height=350, xaxis={"visible": False}, yaxis={"visible": False})
    return figure


app = Dash(__name__, title="Пассажиропоток")
variant_label = f"{int(df['variant'].iloc[0]):02d}" if not df.empty else "не загружен"
card_style = {"background": "#ffffff", "padding": "20px", "borderRadius": "12px", "flex": "1 1 220px"}

app.layout = html.Main(
    [
        html.H1("Пассажиропоток городских маршрутов", style={"marginBottom": "8px"}),
        html.P(f"Вариант {variant_label} · Учебные синтетические данные за 1–21 октября 2026 года"),
        html.Label("Выберите маршрут", htmlFor="route-filter"),
        dcc.Dropdown(
            id="route-filter",
            options=[{"label": "Все маршруты", "value": "all"}]
            + [{"label": f"Маршрут {route}", "value": route} for route in route_names],
            value="all",
            clearable=False,
            style={"maxWidth": "420px", "marginTop": "8px", "marginBottom": "22px", "color": "#172338"},
        ),
        html.Div(
            [
                html.Section([html.Div("Пассажиров за период"), html.H2(id="passenger-total")], style=card_style),
                html.Section([html.Div("Доля рейсов с опозданием"), html.H2(id="delay-rate")], style=card_style),
            ],
            style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "18px"},
        ),
        html.Div(
            [
                html.Section([dcc.Graph(id="daily-chart")], style={**card_style, "flex": "2 1 440px", "minWidth": 0}),
                html.Section([dcc.Graph(id="route-chart")], style={**card_style, "flex": "1 1 320px", "minWidth": 0}),
            ],
            style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
        ),
        html.P("Источник: data.csv. Одна строка — один маршрут за один день.", style={"color": "#52647c"}),
    ],
    style={"maxWidth": "1240px", "margin": "0 auto", "padding": "28px", "fontFamily": "Arial, sans-serif", "color": "#172338", "background": "#f0f4f9", "borderRadius": "16px"},
)


@app.callback(
    Output("passenger-total", "children"),
    Output("delay-rate", "children"),
    Output("daily-chart", "figure"),
    Output("route-chart", "figure"),
    Input("route-filter", "value"),
)
def update_dashboard(selected_route):
    """Обновляет показатели и оба графика при выборе маршрута."""
    if df.empty:
        message = "Загрузите данные: выполните TODO 1"
        return "—", "—", empty_figure(message), empty_figure(message)

    filtered = df.copy()
    # TODO 3. Оставляем строки выбранного маршрута.
    if selected_route != "all":
        filtered = filtered[filtered["route"] == selected_route].copy()

    if filtered.empty:
        return "0", "0.0 %", empty_figure("Нет данных"), empty_figure("Нет данных")

    # TODO 4. Сумма пассажиров за весь выбранный период.
    passenger_total = filtered["passengers"].sum()

    # TODO 5. Доля опоздавших рейсов считается по суммам, а не как среднее процентов.
    delay_rate = 100 * filtered["delayed_trips"].sum() / filtered["trips"].sum()

    # TODO 6. Суммируем пассажиров по датам и строим линию.
    daily = (
        filtered.groupby("date", as_index=False)["passengers"]
        .sum()
        .sort_values("date")
    )
    line = px.line(
        daily,
        x="date",
        y="passengers",
        title="Пассажиры по дням",
        labels={"date": "Дата", "passengers": "Количество пассажиров"},
        markers=True,
    )

    # TODO 7. Суммируем пассажиров по маршрутам и строим столбцы.
    by_route = filtered.groupby("route", as_index=False)["passengers"].sum()
    bar = px.bar(
        by_route,
        x="route",
        y="passengers",
        title="Пассажиры по маршрутам",
        labels={"route": "Маршрут", "passengers": "Количество пассажиров"},
    )

    # Оформление и порядок возвращаемых значений.
    line.update_layout(template="plotly_white", height=350, margin={"l": 45, "r": 15, "t": 55, "b": 45})
    bar.update_layout(template="plotly_white", height=350, margin={"l": 45, "r": 15, "t": 55, "b": 45})
    return f"{passenger_total:,.0f}".replace(",", " "), f"{delay_rate:.1f} %", line, bar


if __name__ == "__main__":
    app.run(debug=True)
