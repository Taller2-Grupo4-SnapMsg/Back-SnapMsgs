import React from 'react'
import { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Image, FlatList, Pressable, RefreshControl } from 'react-native'
import { useNavigation } from '@react-navigation/native';
import { Entypo } from '@expo/vector-icons';
import { db } from '../../firebase';
import { query, orderByChild, equalTo, or, limitToLast, get, ref } from 'firebase/database';
import { useUser } from '../../contexts/UserContext';

AMOUNT_MSGS_BEGINNING = 10

export default Chats = () => { 
  const navigation = useNavigation();
  const { loggedInUser } = useUser();
  const [chats, setChats] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    handleRefresh();
  }, []);


  const handlePressPlus = () => {
    navigation.push('NewChat');
  };

  const handleRefresh = async () => {
    if (loading) return;


    setLoading(true);
    const chatsRef = ref(db, 'chats');
    const email = loggedInUser.email;
    
    try {
      const user1Query = query(chatsRef, orderByChild('user1Email'), equalTo(email));
      const user2Query = query(chatsRef, orderByChild('user2Email'), equalTo(email));
  
      const user1Chats = await get(user1Query);
      const user2Chats = await get(user2Query);
  
      const user1ChatsData = user1Chats.exists() ? user1Chats.val() : {};
      const user2ChatsData = user2Chats.exists() ? user2Chats.val() : {};
  
      const chatData = { ...user1ChatsData, ...user2ChatsData };
  
      const chatList = Object.keys(chatData).map((chatId) => ({
        chatId,
        ...chatData[chatId],
      }));
  
      setChats(chatList);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching chats:', error);
      setLoading(false);
    }
  };

  const renderItem = ({ item }) => {
    const handleChatPress = () => {

    // Navigate to the 'messages' node
    // Retrieve the 20 most recent messages for the selected chat
    const chatID = item.chatID;

    navigation.push('SpecificChat', { chatID: chatID });
  };

    if (item.user1Email === loggedInUser.email) {
      return (
        <TouchableOpacity onPress={handleChatPress}>
          <View style={styles.row}>
            <Image source={{ uri: item.user2Avatar }} style={styles.pic} />
            <View>
              <View style={styles.nameContainer}>
                <Text style={styles.nameTxt} numberOfLines={1} ellipsizeMode="tail">
                  {item.user2Username}
                </Text>
                <Text style={styles.mblTxt}>Mobile</Text>
              </View>
            </View>
          </View>
        </TouchableOpacity>
      );
    } else {
      return (
        <TouchableOpacity onPress={handleChatPress}>
          <View style={styles.row}>
            <Image source={{ uri: item.user1Avatar }} style={styles.pic} />
            <View>
              <View style={styles.nameContainer}>
                <Text style={styles.nameTxt} numberOfLines={1} ellipsizeMode="tail">
                  {item.user1Username}
                </Text>
                <Text style={styles.mblTxt}>Mobile</Text>
              </View>
            </View>
          </View>
        </TouchableOpacity>
      );
    }
    };


  return (
    <View style={{ flex: 1 }}>
      <FlatList
        data={chats}
        keyExtractor={item => {
          return item.chatID; // Make sure to convert the ID to a string
        }}
        renderItem={renderItem} // Use the renderItem function directly
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => handleRefresh()}
            colors={['#947EB0']}
          />
        }
      />
      <Pressable style={styles.floatingButton} onPress={handlePressPlus}>
      <Entypo
        name="plus"
        size={24}
        color="white"
      />
    </Pressable>
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
  },
  floatingButton: {
    backgroundColor: '#B8ADCC',
    borderRadius: 50,
    width: 50,
    height: 50,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'absolute',
    right: 25,
    bottom: 55,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
})