// Quiero un search bar para buscar por username (endpoint hecho)
// y abajo que aparezca automáticamente un listado de la gente a la que yo sigo, como un easy access
// el tema es que este segundo endpoint no está, ver ese tema

import React from 'react'
import { useState, useEffect } from 'react'
import { StyleSheet, Text, View, TouchableOpacity, Image, FlatList, 
  Keyboard } from 'react-native'
import { useNavigation } from '@react-navigation/native';
import SearchBar from '../../components/SearchBar';
import searchUserByUsername from '../../handlers/searchUserByUsername';
import getFollowings from '../../handlers/getFollowings';
import { useUser } from '../../contexts/UserContext';
import { db } from '../../firebase';
import { ref } from 'firebase/database';
import { query, orderByChild, limitToLast, get, set, serverTimestamp } from 'firebase/database';


export default NewChat = () => { 
    const navigation = useNavigation();
    const { loggedInUser } = useUser();
    const [usernameSearched, setUsernameSearched] = useState("");
    const [users, setUsers] = useState([]);

    // Para levantar los users que inicialmente se van a mostrar.
    // Me gustaría que fuesen aquellos a los que sigo, pero la Historia de Usuario no dice nada al respecto
    useEffect(() => {
      const fetchInitialUsers = async () => {
        try {
          const followingsData = await getFollowings(loggedInUser.email);
  
          const simplifiedData = followingsData.map(following => ({
            email: following.email,
            username: following.username,
            avatar: following.avatar,
          }));
  
          setUsers(simplifiedData);
        } catch (error) {
          // Handle any errors here
          console.error('Error fetching data:', error);
        }
      };
  
      fetchInitialUsers(); // Call the async function immediately
  
    }, []);
  

    function generateChatID(user1, user2) {
      // Sort user IDs alphabetically to ensure consistency
      const sortedUserIDs = [user1, user2].sort();
      return `${sortedUserIDs[0].replace(/[\.\#\$\/\[\]]/g, '_')}_${sortedUserIDs[1].replace(/[\.\#\$\/\[\]]/g, '_')}`;
    }

  const renderItem = ({ item }) => {
    const handleChatPress = () => {
      const chatID = generateChatID(loggedInUser.email, item.email);
      const chat = ref(db, `chats/${chatID}`);

      get(chat)
        .then((snapshot) => {
          if (snapshot.exists()) {
            // The chat exists, you can proceed with the query
            const chatRef = ref(db, `chats/${chatID}/messages`); // Navigate to the 'messages' node
            const messageQuery = query(
              chatRef,
              orderByChild('timestamp'),
              limitToLast(20)
            );
            // The chat already exists; handle it as needed
            get(messageQuery)
            .then((snapshot) => {
              if (snapshot.exists()) {
                const messages = Object.values(snapshot.val());
                navigation.push('SpecificChat', { chatID: chatID });
              } else {
                // No messages found
                navigation.push('SpecificChat', { chatID: chatID });
              }
            })
            .catch((error) => {
              console.error("hubo un error al crear la conver3!! ", error);
              // Handle the error
            });
            
          } else {
            // The chat doesn't exist; create it
            const currentTimestamp = serverTimestamp();
            set(chat, {
              chatID: chatID,
              user1Email: loggedInUser.email,
              user2Email: item.email,
              user1Username: loggedInUser.username,
              user2Username: item.username,
              user1Avatar: loggedInUser.avatar,
              user2Avatar: item.avatar,
              timestamp: currentTimestamp,
              messages: [],
            }).then(() => {
              // chat created successfully
              navigation.push('SpecificChat', { chatID: chatID });
            }).catch((error) => {
              console.log("hubo un error al crear la conver!!");
              // Handle the error
            });
          }
        })
        .catch((error) => {
          console.error("hubo un error al crear la conver2!! ", error);
          // Handle the error
        });
    };

    return (
      <TouchableOpacity onPress={handleChatPress}>
        <View style={styles.row}>
          <Image source={{ uri: item.avatar }} style={styles.pic} />
          <View>
            <View style={styles.nameContainer}>
              <Text style={styles.nameTxt} numberOfLines={1} ellipsizeMode="tail">
                {item.username}
              </Text>
              <Text style={styles.mblTxt}>Mobile</Text>
            </View>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  const handleSearchButtonFunction = async () => {
    Keyboard.dismiss();
    user_data = await searchUserByUsername(usernameSearched, 0, 10);
    // Create a copy of the current users array
    const updatedUsers = [...users];

    // Add the new data from user_data to the copy
    const newUsers = [];

    user_data.forEach((userData) => {
      // Create a new user with the correct format
      const newUser = {
        email: userData.email,
        username: userData.username,
        avatar: userData.avatar,
      };

      // Add the new user to the array
      newUsers.push(newUser);
    });

    // Set the 'users' state with the new array of users
    setUsers(newUsers);
  };
   

  return (
    <View style={{ flex: 1 }}>
      <SearchBar
        searchText={usernameSearched} // Replace with your actual searchText value
        setSearchText={setUsernameSearched} // Replace with your actual setSearchText function
        handleSearchButton={handleSearchButtonFunction} // Replace with your actual handleSearchButton function
      />
      <FlatList
        data={users}
        keyExtractor={item => {
          return item.email; // Make sure to convert the ID to a string
        }}
        renderItem={renderItem} // Use the renderItem function directly
      />
    </View>
    
  );
};


const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    borderColor: '#DCDCDC',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    padding: 10,
  },
  pic: {
    borderRadius: 30,
    width: 60,
    height: 60,
  },
  nameContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: 280,
  },
  nameTxt: {
    marginLeft: 15,
    fontWeight: '600',
    color: '#222',
    fontSize: 18,
    width: 170,
  },
  mblTxt: {
    fontWeight: '200',
    color: '#777',
    fontSize: 13,
  },
  msgContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  msgTxt: {
    fontWeight: '400',
    color: '#008B8B',
    fontSize: 12,
    marginLeft: 15,
  }
})