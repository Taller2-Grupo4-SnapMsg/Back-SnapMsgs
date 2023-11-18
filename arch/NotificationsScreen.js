import React, { useEffect, useState } from 'react';
import { query, orderByChild, limitToLast, ref, get, onChildAdded, off } from 'firebase/database';
import { db } from '../../firebase';
import { useFocusEffect } from '@react-navigation/native';
import NotificationMessage from './NotificationMessage';
import NotificationMention from './NotificationMention';
import { useUser } from '../../contexts/UserContext';
import { View, Text, FlatList, RefreshControl, StyleSheet } from 'react-native';

const AMOUNT_NOTIFICATIONS = 10;

function generateUserEmailID(user_receiver_email) {
  return `${user_receiver_email.replace(/[\.\#\$\/\[\]]/g, '_')}`;
}

const NotificationsScreen = () => {
  const { loggedInUser } = useUser();
  const [notifications, setNotifications] = useState([]);
  const notificationsRef = ref(db, `notifications/${generateUserEmailID(loggedInUser.email)}`);
  console.log("notificationsRef: ", notificationsRef)
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [oldestTimeStamp, setOldestTimeStamp] = useState(null);

  const handleGetMoreNotifications = async (refresh) => {
    if (loadingMore) return;

    try {
      setLoadingMore(true);
      setRefreshing(refresh);

      const queryRef = query(
        notificationsRef,
        orderByChild('timestamp'),
        limitToLast(AMOUNT_NOTIFICATIONS)
      );

      if (oldestTimeStamp) {
        queryRef.endAt(oldestTimeStamp - 1);
      }

      const snapshot = await get(queryRef);

      if (snapshot.exists()) {
        const notificationsArray = Object.values(snapshot.val()).reverse();
        if (notificationsArray.length > 0) {
          const newOldestTimestamp = notificationsArray[0].timestamp;
          setOldestTimeStamp(newOldestTimestamp);

          if (refresh) {
            setNotifications(notificationsArray);
          } else {
            setNotifications((prevNotifications) => [...prevNotifications, ...notificationsArray]);
          }
        }
      }
    } catch (error) {
      console.error('Error while loading more notifications:', error);
    } finally {
      setLoadingMore(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    React.useCallback(() => {
      handleGetMoreNotifications((new Date()).getTime(), true);
    }, [])
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Notifications</Text>
      <FlatList
        data={notifications}
        keyExtractor={(item) => item.identifier}
        renderItem={({ item }) => (
          <View style={styles.notificationContainer}>
            {item.type === 'notification' ? (
              <NotificationMessage notification={item.body} data={item.data} read={item.read} />
            ) : item.type === 'mention' ? (
              <NotificationMention notification={item.body} data={item.data} read={item.read} />
            ) : null}
            <View style={styles.separator} />
          </View>
        )}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => handleGetMoreNotifications(true)}
            colors={['#947EB0']}
          />
        }
        onEndReached={() => handleGetMoreNotifications(false)}
        onEndReachedThreshold={0.1}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  notificationContainer: {
    marginBottom: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  separator: {
    marginVertical: 10,
  },
});

export default NotificationsScreen;

