const regions = [
    ['1', 'ACEH'],
    ['6728', 'SUMATERA UTARA'],
    ['12920', 'SUMATERA BARAT'],
    ['14086', 'RIAU'],
    ['15885', 'JAMBI'],
    ['17404', 'SUMATERA SELATAN'],
    ['20802', 'BENGKULU'],
    ['22328', 'LAMPUNG'],
    ['24993', 'KEPULAUAN BANGKA BELITUNG'],
    ['25405', 'KEPULAUAN RIAU'],
    ['25823', 'DKI JAKARTA'],
    ['26141', 'JAWA BARAT'],
    ['32676', 'JAWA TENGAH'],
    ['41863', 'DAERAH ISTIMEWA YOGYAKARTA'],
    ['42385', 'JAWA TIMUR'],
    ['51578', 'BANTEN'],
    ['53241', 'BALI'],
    ['54020', 'NUSA TENGGARA BARAT'],
    ['55065', 'NUSA TENGGARA TIMUR'],
    ['58285', 'KALIMANTAN BARAT'],
    ['60371', 'KALIMANTAN TENGAH'],
    ['61965', 'KALIMANTAN SELATAN'],
    ['64111', 'KALIMANTAN TIMUR'],
    ['65702', 'SULAWESI UTARA'],
    ['67393', 'SULAWESI TENGAH'],
    ['69268', 'SULAWESI SELATAN'],
    ['72551', 'SULAWESI TENGGARA'],
    ['74716', 'GORONTALO'],
    ['75425', 'SULAWESI BARAT'],
    ['76096', 'MALUKU'],
    ['77085', 'MALUKU UTARA'],
    ['78203', 'PAPUA'],
    ['81877', 'PAPUA BARAT'],
    ['928068', 'KALIMANTAN UTARA'],
    ['-99', '+Luar Negeri']
]

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

function format_name_to_id(name) {
    return name.replace(/[^A-Z0-9]+/ig, "").toLowerCase()
}

function createStackbarChart(chartId, response = {}, title = "Memuat data grafik . . .") {
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
            series:{
                maxPointWidth: 15
            },
            column: {
                stacking: 'normal'
            },
            columnrange: {
                grouping: false
            }
        },

        series: response.series || []
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

function createPieChart(chartId, response = {}, title = "Memuat data grafik . . .") {
    Highcharts.setOptions({
        colors: ['#ffc107', '#17a2b8', '#28a745', '#dc3545', '#6f42c1', '#e83e8c']
    });
    Highcharts.chart(chartId, {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            events: {
                load: function () {
                    let processTps = response.process_tps || 0
                    let totalTps = response.total_tps || 0
                    let textLabel = `Terproses ${numberWithCommas(processTps)} dari ${numberWithCommas(totalTps)} TPS <b>(${response.percentage_tps || 0}%)</b>`
                    var label = this.renderer.label(textLabel)
                        .css({
                            width: '400px',
                            fontSize: '12px'
                        })
                        .attr({
                            'stroke': 'black',
                            'stroke-width': 1,
                            'r': 2,
                            'padding': 8
                        })
                        .add();

                    label.align(Highcharts.extend(label.getBBox(), {
                        align: 'center',
                        verticalAlign: 'top',
                        y: 75, // offset
                    }), null, 'spacingBox');

                },
            },
            marginTop: 175,
            marginBottom: 175,
            type: 'pie'
        },
        title: {
            text: title
        },
        tooltip: {
            pointFormat: '<b>{point.percentage:.2f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b> <br>Perolehan suara: {point.percentage:.2f} %',
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                    }
                }
            }
        },
        series: typeof response.series === 'undefined' ? [] : response.series
    })
}

function requestJson(url, callback) {
    $.ajax({
        url: url,
        type: 'GET',
        async: true,
        dataType: "json",
        success: function (response) {
            callback(response)
        }
    });
}

$(document).ready(function () {
    createStackbarChart("#range_chart")
    createStackbarChart("#range_merge_chart")

    createPieChart("accumulation_chart")

    requestJson("/api/pemilu2019/chart/range", function (response) {
        createStackbarChart("#range_chart", response, response.title)
    })

    requestJson("/api/pemilu2019/chart/range/merge", function (response) {
        createStackbarChart("#range_merge_chart", response, response.title)
    })

    requestJson("/api/pemilu2019/chart/total", function (response) {
        createPieChart("accumulation_chart", response, response.title)
    })

    for (reg of regions) {
        createStackbarChart(`#${format_name_to_id(reg[1])}`)
        requestJson(`/api/pemilu2019/chart/range/region?code=${reg[0]}&target=${format_name_to_id(reg[1])}`, function (response) {
            createStackbarChart(`#${response.target}`, response, response.title)
        })
    }
});