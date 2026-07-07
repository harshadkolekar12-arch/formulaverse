importScripts('https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging-compat.js');

firebase.initializeApp({
    apiKey: "AIzaSyDEO2NDNQZgt9NshLFIhYntGOafMQtdQBA",
    authDomain: "formulaverse-afaf2.firebaseapp.com",
    projectId: "formulaverse-afaf2",
    storageBucket: "formulaverse-afaf2.firebasestorage.app",
    messagingSenderId: "472325603873",
    appId: "1:472325603873:web:06fbd627b03c3d0c3b5960"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
    const { title, body, icon } = payload.notification;
    self.registration.showNotification(title, {
        body: body,
        icon: icon || '/static/formulas/icon-192.png',
        badge: '/static/formulas/icon-192.png',
        vibrate: [200, 100, 200],
    });
});