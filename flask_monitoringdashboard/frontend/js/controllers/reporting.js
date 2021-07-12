export function ReportingController($scope, $http, menuService, endpointService, plotlyService) {
    endpointService.reset();
    menuService.reset('reporting');

    $scope.reports = {};

    $scope.activeSection = 'week';

    $scope.monthName = moment().format('MMMM');
    $scope.previousMonthName = moment().subtract(1, 'months').format('MMMM');

    $scope.currentDay = moment().format('MMM DD');
    $scope.yesterday = moment().subtract(1, 'days').format('MMM DD');

    $scope.currentWeekNumber = moment().isoWeek();
    $scope.previousWeekNumber = moment().subtract(1, 'weeks').isoWeek();

    $scope.generating = false;
    $scope.onlyShowInteresting = true;


    $scope.activeSection = 'custom';
    $scope.intervals = intervals(1, 'months');


    function intervals(q, units) {
        const t1 = moment()
            .subtract(q, units)
            .startOf(units);

        const t2 = moment().subtract(q, units).endOf(units);
        const t3 = moment().startOf(units);
        const t4 = moment().endOf(units);

        return {
            "comparison": {
                "from": t3.toDate(),
                "to": t4.toDate()
            },
            "baseline": {
                "from": t1.toDate(),
                "to": t2.toDate()
            }
        }
    }

    $scope.versions = [];

    $scope.commitVersion = null;
    $scope.baseLineCommitVersion = null;

    $scope.selectSection = function (section) {
        if (section === 'commits') {
            $http.get('api/versions').then(function (response) {
                $scope.versions = response.data;
            })
        }
        $scope.activeSection = section;

        const INTERVAL_SIZES = {
            day: [1, 'days'],
            week: [1, 'isoWeeks'],
            month: [1, 'months'],
            custom: [1, 'isoWeeks'],
        };

        const intervalSize = INTERVAL_SIZES[$scope.activeSection];

        $scope.intervals = intervals(intervalSize[0], intervalSize[1])
    };

    $scope.selectEntry = function (summary, answer) {
        $scope.selectedSummary = summary;
        $scope.selectedAnswer = answer;

        const {comparison, baseline} = answer.latencies_samples;

        const data = [
            {
                name: `Comparison (N=${comparison.length})`,
                type: 'violin',
                y: comparison
            },
            {
                name: `Baseline (N=${baseline.length})`,
                type: 'violin',
                y: baseline,
            }
        ];


        plotlyService.chart(data, {
            yaxis: {
                title: 'Execution time (ms)',
                rangemode: "nonnegative"
            }
        });
    };

    $scope.generateReport = function () {
        $scope.generating = true;
        $scope.error = '';

        let promise;
        if ($scope.activeSection === 'commits') {
            promise = $http.post('api/reporting/make_report/commits', {
                commit_version: $scope.commitVersion,
                baseline_commit_version: $scope.baseLineCommitVersion,
            })
        } else {
            promise = $http.post(`api/reporting/make_report/intervals`, {
                interval: {
                    to: parseInt(`${$scope.intervals.comparison.to.getTime() / 1000}`),
                    from: parseInt(`${$scope.intervals.comparison.from.getTime() / 1000}`),
                },
                baseline_interval: {
                    to: parseInt(`${$scope.intervals.baseline.to.getTime() / 1000}`),
                    from: parseInt(`${$scope.intervals.baseline.from.getTime() / 1000}`),
                }
            })
        }

        promise.then(response => {
            $scope.reports[$scope.activeSection] = response.data;
            $scope.generating = false;
        })

        promise.catch(response => {
            $scope.error = response.data.message || 'An unknown error occurred!';
            $scope.generating = false;
        })
    };
}
