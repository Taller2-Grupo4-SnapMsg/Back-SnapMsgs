import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createDrawerNavigator } from '@react-navigation/drawer';
import SignInScreen from './screens/signIn/SignInScreen';
import SignUpScreen from './screens/signUp/SignUpScreen';
import Home from './screens/home/Home';
import PostDetailed from './screens/home/PostDetailed';
import NewPost from './screens/home/NewPost/NewPost';
import Profile from './screens/profile/Profile';
import EditProfile from './screens/profile/EditProfile';
import FollowingsList from './screens/profile/FollowingsList';
import FollowersList from './screens/profile/FollowersList';
import Interests from './screens/signUp/Interests';
import Search from './screens/search/Search';
import ProfileEditPost from './screens/profile/ProfileEditPost';
import Statistics from './screens/statistics/Statistics';
import CustomDrawerContent from './components/navigators/CustomerDrawerContent';
import Chats from './screens/chats/Chats';
import SpecificChat from './screens/chats/SpecificChat';
import NewChat from './screens/chats/NewChat';
import NotificationsScreen from './screens/notifications/NotificationsScreen';
import { ref, set, get, update } from 'firebase/database';
import { db } from './firebase';

import { Linking } from 'react-native';

import { useColorScheme } from 'react-native';

import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';

import { useUser } from './contexts/UserContext';

import * as Notifications from 'expo-notifications';
import { useNavigation } from '@react-navigation/native';

const Stack = createStackNavigator();
const Drawer = createDrawerNavigator();
const AuthStack = createStackNavigator();

const StackNavigatorHome = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Home" component={Home} />
      <Stack.Screen name="PostDetailed" component={PostDetailed} />
      <Stack.Screen name="NewPost" component={NewPost} />
      <Stack.Screen name="Profile" component={Profile} />
    </Stack.Navigator>
  );
};

const StackNavigatorNotifications = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="InNotificationsScreen" component={NotificationsScreen} />
      <Stack.Screen name="SpecificChat" component={SpecificChat} />
      <Stack.Screen name="PostDetailedNotification" component={PostDetailed} />
    </Stack.Navigator>
  );
};

const StackNavigatorProfile = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Profile" component={Profile} />
      <Stack.Screen name="EditProfile" component={EditProfile} />
      <Stack.Screen name="FollowingsList" component={FollowingsList} />
      <Stack.Screen name="FollowersList" component={FollowersList} />
      <Stack.Screen name="ProfileEditPost" component={ProfileEditPost} />
    </Stack.Navigator>
  );
};

const StackNavigatorSearch = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Search" component={Search} />
      <Stack.Screen name="Profile" component={Profile} />
      <Stack.Screen name="FollowingsList" component={FollowingsList} />
      <Stack.Screen name="FollowersList" component={FollowersList} />
      <Stack.Screen name="PostDetailed" component={PostDetailed} />
    </Stack.Navigator>
  );
}

const StackNavigatorChats = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Chats" component={Chats} />
      <Stack.Screen name="SpecificChat" component={SpecificChat} />
      <Stack.Screen name="NewChat" component={NewChat} />
    </Stack.Navigator>
  );
}

const AuthNavigator = () => {
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="SignIn" component={SignInScreen} />
      <AuthStack.Screen name="SignUp" component={SignUpScreen} />
    </AuthStack.Navigator>
  );
};

function generateUserEmailID(user_receiver_email) {
  return `${user_receiver_email.replace(/[\.\#\$\/\[\]]/g, '_')}`;
}

function markNotificationAsRead(notificationId, user_receiver) {
  const notifRef = ref(db, `notifications/${generateUserEmailID(user_receiver)}/${notificationId}`);
  get(notifRef)
    .then((snapshot) => {
      if (snapshot.exists()) {
        update(notifRef, { read: true });
      }
    });
}

function handleNotificationResponse(response, navigation) {
  const route = response.notification.request.content.data.route;
  if (route === 'message') {
    const chatID = response.notification.request.content.data.chatID;
    const user_receiver = response.notification.request.content.data.user_sender;
    const user_sender = response.notification.request.content.data.user_receiver;
    markNotificationAsRead(response.notification.request.identifier, user_receiver);
    navigation.navigate('Chat', { chatID, user_receiver, user_sender });
  }
  if (route === 'mention') {
    const user_receiver = response.notification.request.content.data.user_sender;
    const post_id = response.notification.request.content.data.post_id;
    markNotificationAsRead(response.notification.request.identifier, user_receiver);
    navigation.navigate('PostDetailed', { post_id });
  }
}

const MainNavigator = () => {
  console.log("ENTRA A MAIN NAVIGATOR")
  const navigation = useNavigation();

  useEffect(() => {
    // const handleInitialUrl = async () => {
    //   console.log("ENTRA A handleInitialUrl")
    //   const url = await Linking.getInitialURL();

    //   if (url) {
    //     navigation.navigate('Profile');
    //   } else {
        
    //   }
    // };

    const responseListener = Notifications.addNotificationResponseReceivedListener(response => {
      console.log("ENTRA A responseListener")
      handleNotificationResponse(response, navigation);
    });

    //handleInitialUrl();

    return () => {
      Notifications.removeNotificationSubscription(responseListener);
    };
  }, [navigation]);

  return (
    <Drawer.Navigator
      drawerContent={props => <CustomDrawerContent {...props} navigation={props.navigation} />}
    >
      <Drawer.Screen name="InHome" component={StackNavigatorHome}  options={{ title: 'Home' }} />
      <Drawer.Screen name="ProfileDetail" component={StackNavigatorProfile}  options={{ title: 'Profile' }} />
      <Drawer.Screen name="SearchUserScreen" component={StackNavigatorSearch} options={{ title: 'Search' }} />
      <Drawer.Screen name="StatisticsScreen" component={Statistics} options={{ title: 'Statistics' }} />
      <Drawer.Screen name="ChatsScreen" component={StackNavigatorChats} options={{ title: 'Chats' }} />
      <Drawer.Screen name="NotificationsScreen" component={StackNavigatorNotifications} options={{ title: 'Notifications' }} />
      <Drawer.Screen name="Chat" component={SpecificChat}/>
    </Drawer.Navigator>
  );
};


export default function AppComponent() {
  const {loggedInUser} = useUser(); 
  const colorScheme = useColorScheme();
  console.log("ENTRA EN APP COMPONENT")
  
  return (
      <NavigationContainer theme={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
        {loggedInUser ? (
            <AuthStack.Navigator screenOptions={{ headerShown: false }} initialRouteName="MainNavigator">
              <AuthStack.Screen name="MainNavigator" component={MainNavigator} />
              <AuthStack.Screen name="SignIn" component={SignInScreen} />
              <AuthStack.Screen name="SignUp" component={SignUpScreen} />
              <AuthStack.Screen name="Interests" component={Interests} />
            </AuthStack.Navigator>
        ) : (
          <AuthNavigator />
        )}
      </NavigationContainer>
  );
}
