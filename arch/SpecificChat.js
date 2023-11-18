import React, { useState, useRef, useEffect } from 'react'
import {
  StyleSheet,
  Text,
  View,
  Image,
  FlatList,
  Dimensions,
  KeyboardAvoidingView,
  Keyboard,
  RefreshControl
} from 'react-native'
import { TextInput } from 'react-native-paper';
import { useUser } from '../../contexts/UserContext';
import { db } from '../../firebase';
import { query, orderByChild, endAt, get, limitToLast, ref, push, serverTimestamp, onChildAdded, off } from 'firebase/database';
const { width, height } = Dimensions.get('window')

AMOUNT_MSGS_BACK = 5
AMOUNT_MSGS_BEGINNING = 10

export default SpecificChat = ({ route }) => {
  const { loggedInUser } = useUser();
  const chatID = route.params.chatID;
  const [messages, setMessages] = useState([]);
  const [latestTimestamp, setLatestTimestamp] = useState(0);
  const [oldestTimestamp, setOldestTimestamp] = useState(0);
  
  const messagesRef = ref(db, `chats/${chatID}/messages`);
  const [newMessage, setNewMessage] = useState('');
  const flatListRef = useRef(null);
  const [refreshing, setRefreshing] = useState(false);


  const onFlatListLayout = () => {
    setTimeout(() => {
      if (flatListRef.current) {
        flatListRef.current.scrollToEnd({ animated: true });
      }
    }, 100);
  };

  const onChildAddedCallback = (snapshot) => {
    if (snapshot) {
      const newMessage = snapshot.val();
      if (newMessage.timestamp > latestTimestamp) {
        setLatestTimestamp(newMessage.timestamp);
        setMessages((prevMessages) => [...prevMessages, newMessage]);
      }
    }
  };

  useEffect(() => {
    const unsubscribe = onChildAdded(messagesRef, onChildAddedCallback);

    return () => {
      off(messagesRef, 'child_added', onChildAddedCallback);
    };
  }, [messages]);


  useEffect(() => {
    const fetchData = async () => {
      try {
        const messagesRef = ref(db, `chats/${chatID}/messages`);
        const messageQuery = query(
          messagesRef,
          orderByChild('timestamp'),
          limitToLast(AMOUNT_MSGS_BEGINNING)
        );
  
        const snapshot = await get(messageQuery);
        if (snapshot.exists()) {
          const newest_messages = Object.values(snapshot.val());
          setMessages(newest_messages);
          
          setLatestTimestamp(newest_messages[newest_messages.length - 1].timestamp);
          setOldestTimestamp(newest_messages[0].timestamp);
          
          if (flatListRef.current) {
            flatListRef.current.scrollToEnd({ animated: true });
          }
        } else {
          setMessages([]);
          setLatestTimestamp(0);
          setOldestTimestamp(0);
        }
      } catch (error) {
        // handle error
      }
    };
  
    fetchData();
  }, []);
  
  const handleGetOlderMsgs = async () => {
    if (refreshing) return;

    setRefreshing(true);
    
    const queryRef = query(
      messagesRef,
      orderByChild('timestamp'),
      endAt(oldestTimestamp - 1), 
      limitToLast(AMOUNT_MSGS_BACK)
    );

    try {
      const snapshot = await get(queryRef);
      if (snapshot.exists()) {
        const messageArray = [];
        snapshot.forEach((childSnapshot) => {
          const message = childSnapshot.val();
          messageArray.push(message);
        });
        if (messageArray.length > 0) {
          const newMessages = [...messageArray, ...messages];
          setMessages(newMessages);
          setOldestTimestamp(messageArray[0].timestamp);
        }
      }

      setRefreshing(false);
    } catch (error) {
      console.error('Error fetching earlier messages:', error);
    }
  };

  const send = () => {
    if (newMessage.length > 0) {
      Keyboard.dismiss();
      const currentTimestamp = serverTimestamp();
      const newDBMessage = {
        text: newMessage,
        sender: loggedInUser.email,
        timestamp: currentTimestamp,
        avatar: loggedInUser.avatar,
      };

      push(messagesRef, newDBMessage)
      .then(() => {
        setNewMessage('')
      
        if (flatListRef.current) {
          flatListRef.current.scrollToEnd();
        }
      })
      .catch((error) => {
        // Handle the error, e.g., display an error message
      });
    }
  }

  const renderItem = ({ item }) => {
    if (item.sender === loggedInUser.email) {
      return (
        <View style={styles.rightMsg}>
          <View style={styles.rightBlock}>
            <Text style={styles.rightTxt}>{item.text}</Text>
          </View>
          <Image source={{ uri: loggedInUser.avatar }} style={styles.userPic} />
        </View>
      )
      
    } else {
      return (
        <View style={styles.eachMsg}>
          <Image source={{ uri: item.avatar }} style={styles.userPic} />
          <View style={styles.msgBlock}>
            <Text style={styles.msgTxt}>{item.text}</Text>
          </View>
        </View>
      )
    }
  }

  return (
    <KeyboardAvoidingView behavior="padding" enabled style={styles.container}> 
      <FlatList
      ref={flatListRef}
      style={styles.list}
      extraData={messages}
      data={messages}
      keyExtractor={(item) => item.timestamp}
      renderItem={renderItem}
      keyboardShouldPersistTaps="handled"
      onLayout={onFlatListLayout}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={handleGetOlderMsgs}
          colors={['#947EB0']}
        />
      }
    />

      <View style={styles.input}>
        <TextInput
          style={styles.inputText}
          placeholderTextColor="#696969"
          onChangeText={msg => setNewMessage(msg)}
          value={newMessage} 
          blurOnSubmit={true}
          onSubmitEditing={() => send()}
          placeholder="Type a message"
          returnKeyType="send"
        />
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  list: {
    flex: 1,
  },
  keyboard: {
    flex: 1,
    justifyContent: 'center',
  },
  image: {
    width,
    height,
  },
  header: {
    height: 65,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#075e54',
  },
  left: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  right: {
    flexDirection: 'row',
  },
  chatTitle: {
    color: '#fff',
    fontWeight: '600',
    margin: 10,
    fontSize: 15,
  },
  chatImage: {
    width: 30,
    height: 30,
    borderRadius: 15,
    margin: 5,
  },
  input: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 15,
    padding: 5,
    margin: 20,
  },
  inputText: {
    flex: 1,
    height: 30,
  },
  eachMsg: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    margin: 5,
  },
  rightMsg: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    margin: 5,
    alignSelf: 'flex-end',
  },
  userPic: {
    height: 40,
    width: 40,
    margin: 5,
    borderRadius: 20,
    backgroundColor: '#f8f8f8',
  },
  msgBlock: {
    width: 220,
    borderRadius: 5,
    backgroundColor: '#ffffff',
    padding: 10,
    shadowColor: '#3d3d3d',
    shadowRadius: 2,
    shadowOpacity: 0.5,
    shadowOffset: {
      height: 1,
    },
  },
  rightBlock: {
    width: 220,
    borderRadius: 5,
    backgroundColor: '#B8ADCC',
    padding: 10,
    shadowColor: '#3d3d3d',
    shadowRadius: 2,
    shadowOpacity: 0.5,
    shadowOffset: {
      height: 1,
    },
  },
  msgTxt: {
    fontSize: 15,
    color: '#555',
    fontWeight: '600',
  },
  rightTxt: {
    fontSize: 15,
    color: '#202020',
    fontWeight: '600',
  },
})