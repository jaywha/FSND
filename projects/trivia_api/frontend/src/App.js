import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch
} from 'react-router-dom'

// import logo from './logo.svg';
import './stylesheets/App.css';
import QuestionFormView from './components/QuestionFormView';
import CategoryFormView from "./components/CategoryFormView";
import QuestionView from './components/QuestionView';
import Header from './components/Header';
import QuizView from './components/QuizView';
import 'bootstrap/dist/css/bootstrap.min.css';


class App extends Component {
  render() {
    return (
    <div className="App">
      <Header path />
      <Router>
        <Switch>
          <Route path="/" exact component={QuestionView} />
          <Route path="/questions/add" component={QuestionFormView} />
          <Route path="/categories/add" component={CategoryFormView} />
          <Route path="/play" component={QuizView} />
          <Route component={QuestionView} />
        </Switch>
      </Router>
    </div>
  );

  }
}

export default App;
