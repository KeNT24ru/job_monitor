// ********
// Main App
// ********

var JobMonitorApp = angular
    .module('JobMonitorApp', ['ngCookies'])
    .config(function($httpProvider) {
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';

        $httpProvider.defaults.transformRequest = function(data) {
            if (data === undefined) {
                return data;
            } else {
                return $.param(data);
            }
        }
        $httpProvider.defaults.headers.post['Content-Type'] =
            'application/x-www-form-urlencoded; charset=UTF-8';
    });


// *******
// Filters
// *******

JobMonitorApp.filter('linebreaks', function($sce) {
    return function(data) {
        return $sce.trustAsHtml(data.replace(/\n/, '<br>'));
    }
});


JobMonitorApp.filter('highlight', function ($sce) {
    return function (text, keywords) {
        angular.forEach(keywords, function(keyword, idx) {
            text = text.replace(new RegExp(keyword, 'gi'), '<span class="highlight-match">$&</span>');
        });
        return $sce.trustAsHtml(text);
    }
});


// **********************
// Notification Contoller
// **********************

JobMonitorApp.controller('NotificationController', ['$scope', function($scope) {
    $scope.messages = [];

    $scope.$on('notification', function(event, message){
        message.id = Math.random();
        $scope.messages.push(message);
    });

    $scope.closeMessage = function(mid) {
        $scope.messages = $scope.messages.filter(function(elem) {
            return elem.id != mid;
        });
    }
}]);


// ***********************
// Project List Controller
// ***********************

JobMonitorApp.controller('ProjectListController', ['$scope', '$rootScope', '$http', function($scope, $rootScope, $http) {
    $scope.searchConfig = {
        'status': 'new',
        'tag': 'start-up',//web scraping',
        'service': 'all',
    };

    $scope.refreshProjectList = function(query) {
        angular.forEach(query, function(value, key) {
            $scope.searchConfig[key] = value;
        });
        params = {
            'status': $scope.searchConfig['status'],
            'tag': $scope.searchConfig['tag'],
            'service': $scope.searchConfig['service']
        }
        $http({'method': 'GET', 'url': '/api/project', 'params': params}).success(function(data) {
            $scope.projects = data.projects;
            $scope.highlight_keywords = data.highlight_keywords;
            $scope.tags = data.tags;
            $scope.services = data.services;
            $scope.statuses = data.statuses;
        });
    }

    $scope.markVisibleProjectsRead = function() {
        params = {
            'status': $scope.searchConfig['status'],
            'tag': $scope.searchConfig['tag'],
            'service': $scope.searchConfig['service'],
            'update_status': 'read'
        }
        $http({'method': 'POST', 'url': '/api/project/bulk', 'data': params}).success(function(data) {
            if (data.messages) {
                angular.forEach(data.messages, function(msg, idx) {
                    $rootScope.$broadcast('notification', msg);
                });
            }
            $scope.refreshProjectList();
        });
    }

    $scope.markProjectRead = function(projectId) {
        params = {
            'project_id': projectId,
            'update_status': 'read'
        }
        $http({'method': 'POST', 'url': '/api/project/update', 'data': params}).success(function(data) {
            if (data.messages) {
                angular.forEach(data.messages, function(msg, idx) {
                    $rootScope.$broadcast('notification', msg);
                });
            }
            $scope.refreshProjectList();
        });
    }

    $scope.refreshProjectList();
}]);
