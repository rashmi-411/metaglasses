// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAAVG9i88HBW7Ho2vzqecr4rQwKI-bTSGQ",
  authDomain: "metaglasses-cc207.firebaseapp.com",
  projectId: "metaglasses-cc207",
  storageBucket: "metaglasses-cc207.firebasestorage.app",
  messagingSenderId: "691125419159",
  appId: "1:691125419159:web:79ef15c3509ba2f5607dd2",
  measurementId: "G-5C5LB3CKTW"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);