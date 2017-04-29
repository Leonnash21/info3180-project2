/* Angular module and controllers for Wishlist App */

/* -------------------------------------------------
 * INITIALISATION
 * -------------------------------------------------
 */
var WISHLIST_SETTINGS = {title_suffix: ' - StarGaze'};
var WishlistApp = angular.module('starGaze', ['ui.router',])
    .config(function($locationProvider){
        $locationProvider.html5Mode(false).hashPrefix('!');
    })
    .config(function ($httpProvider) {
        // set any default headers here
        // $http.defaults.headers.common['X-Custom-header'] = "some value"
		angular.extend($httpProvider.defaults.headers.common,
				{'X-Requested-With': 'XMLHttpRequest', 'X-JSClient': 'stargaze-official'});

//      IF we want to add default headers only for get requests:
// 		if (!$httpProvider.defaults.headers.get) {
// 			$httpProvider.defaults.headers.get = {};
// 		}

	})
    .config(function($stateProvider){
        // ToDo: Put route config here
        // $routeProvider
        //     .when('/register', {templateUrl: '/forms/register.html',
        //           controller: 'RegistrationCtrl', title:'Register/Signup'});
        var registerState = {name: 'register', url: '/register', 
            templateUrl: '/forms/register.html', title:'Register/Signup',
            controller: 'RegistrationCtrl'
        };
        $stateProvider.state({name: 'login', url:'/login',
                templateUrl: '/forms/login.html', title: 'StarGaze Login',
                controller: 'LoginCtrl'});

        $stateProvider.state(registerState);
    })
    .run(function($rootScope, $http, $state, $timeout, $document){
        // set any default headers here
        // $http.defaults.headers.common['X-Custom-header'] = "some value"
        
        $rootScope.$on('$stateChangeSuccess',
            function(event, to, toparm, fr, fromparms){
                // this function sets up the browser title based on the 
                // ui.state that was loaded
                var t = 'No title yet';
                if (to.title){
                    t = (typeof(to.title) == 'function')? to.title(to, fr) : to.title;
                }
                $document[0].title = '' + t + WISHLIST_SETTINGS.title_suffix;
            });

    });


/* -------------------------------------------------
 * SERVICES
 * -------------------------------------------------
 */


/* -------------------------------------------------
 * COMPONENTS
 * -------------------------------------------------
 */


/* -------------------------------------------------
 * CONTROLLERS
 * -------------------------------------------------
 */

// Main Controller that handles the overall page
WishlistApp.controller('MainCtrl', ['$scope', '$state', '$http',
function($scope, $state, $http){
    
}]);

// Registration Controller
WishlistApp.controller('RegistrationCtrl', ['$scope', '$state', '$http',
function($scope, $state, $http){
    $scope.SignupForm = {};
    $scope.checkAddProfile = function(){
        // this function will make the http request to create the user
    }
}]);

// Login Form Controller
WishlistApp.controller('LoginCtrl', ['$scope', '$state', '$http',
function($scope, $state, $http){
    
    $scope.doLogin = function() {
        // call the HTTP thingy to perform the actual login
        
    }
}]);

// Controller to add a wishlist item
WishlistApp.controller('AddWishCtrl', ['$scope', '$state', '$http',
function($scope, $state, $http){
    
    
    $scope.fetchThumbs = function(){
        // this method gets a list of thumbnail urls from the server
    }
    $scope.doAddWish = function(){
        // this function adds an item to the wishlist - http post?
    }
    
}])
