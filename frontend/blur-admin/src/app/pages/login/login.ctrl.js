(function () {
  'use strict';

  angular.module('BlurAdmin.pages.login')
    .controller('loginCtrl', function($scope, $auth, $rootScope, $window, $location, $httpParamSerializerJQLike) {

      $scope.login = function() {

      $scope.alert = false;
      document.getElementById('inputEmail3').focus()

      var user = {
        email: $scope.email,
        password: $scope.password
      };

      var requestConfig = {
        url: "/api/auth/login",
        headers: {'Content-Type': 'application/json'},
        data: $httpParamSerializerJQLike(user),
      };

      $auth.login(user, requestConfig)
        .then(function(response) {
          // set the token and move on
          $auth.setToken(JSON.stringify(response.data.auth_token));
          $location.path('/dashboard');
        })
        .catch(function(response) {
          $scope.email = '';
          $scope.password = '';
          document.getElementById('inputEmail3').focus()
          $scope.alert = true;
        });
    };

  });

})();