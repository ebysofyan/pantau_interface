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
                let idx = this.point.index
                let total_title = typeof response.total_title === 'undefined' ? "" : '<p>' + response.total_title + ' : <b>' + numberWithCommas(this.y) + '</b></p><br/>'
                let server_date = typeof this.series.options.server_date === 'undefined' ? [] : this.series.options.server_date
                let kpu_ts = typeof this.series.options.kpu_ts === 'undefined' ? [] : this.series.options.kpu_ts
                let nolsatu_data = typeof this.series.options.nolsatu_data === 'undefined' ? [] : this.series.options.nolsatu_data
                let noldua_data = typeof this.series.options.noldua_data === 'undefined' ? [] : this.series.options.noldua_data
                let main_data = typeof this.series.options.main_data === 'undefined' ? [] : this.series.options.main_data
                let total_main_title = typeof response.total_main_title === 'undefined' ? "" : '<p>' + response.total_main_title + ' : <b>' + numberWithCommas(main_data[idx]) + '</b></p><br/>'

                let nolsatu_data_format = nolsatu_data.length === 0 ? "" : '<p>Suara paslon 01' + ' : <b>' + numberWithCommas(nolsatu_data[idx]) + '</b></p><br/>'
                let noldua_data_format = noldua_data.length === 0 ? "" : '<p>Suara paslon 02' + ' : <b>' + numberWithCommas(noldua_data[idx]) + '</b></p><br/>'

                return '<p></p><b>' + this.x + ' ' + this.series.options.stack + '</b></p><br/><br/>'
                    + '<p>' + server_date + '</p><br/>'
                    + '<p>' + kpu_ts + '</p><br/><br/>'
                    + nolsatu_data_format
                    + noldua_data_format
                    + total_main_title
                    + total_title
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
    requestJson("#range_merge_chart", "/api/pemilu2019/chart/range/merge")
    requestJson("#accumulation_chart", "/api/pemilu2019/chart/acc")
});