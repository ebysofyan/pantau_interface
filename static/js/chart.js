function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

function createChart(chartId, response = {}, title = "Memuat data grafik . . .") {
    var options = {

        chart: {
            type: 'column'
        },

        title: {
            text: title
        },

        xAxis: [{
            categories: typeof response.bt_categories === 'undefined' ? [] : response.bt_categories
        },
        {
            categories: typeof response.tp_categories === 'undefined' ? [] : response.tp_categories,
            opposite: true
        }],

        yAxis: {
            allowDecimals: false,
            min: 0,
            title: false,
            labels: false
        },

        tooltip: {
            formatter: function () {
                let total_title = typeof response.total_title === 'undefined' ? "" : response.total_title
                return '<b>' + this.x + ' ' + this.series.options.stack + '</b><br/>'
                    + this.series.name + '<br/>'
                    + '<p><b>' + total_title + ' : ' + numberWithCommas(this.y) + '</p>' + '<br/>'
            }
        },

        plotOptions: {
            column: {
                stacking: 'normal'
            },
            columnrange: {
                grouping: false
            }
        },

        series: typeof response.series === 'undefined' ? [] : response.series
    };

    var onLegendClick = function (event) {
        var myname = this.name;
        var myvis = !this.visible;
        this.chart.series.forEach(function (elem) {
            if (elem.name == myname) {
                elem.setVisible(myvis);
            }
        });
        return false;
    }


    options.series.forEach(function (serie) {
        serie.events = { legendItemClick: onLegendClick };
    });
    $(chartId).highcharts(options);
};

function requestJson(chartId, url) {
    createChart(chartId)

    $.ajax({
        url: url,
        type: 'GET',
        async: true,
        dataType: "json",
        success: function (response) {

            createChart(chartId, response, response.title)
        }
    });
}

$(document).ready(function () {
    requestJson("#range_chart", "/api/pemilu2019/chart/range")
    requestJson("#accumulation_chart", "/api/pemilu2019/chart/acc")
});