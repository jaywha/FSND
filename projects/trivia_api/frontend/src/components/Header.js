import React, { Component } from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import NavDropdown from "react-bootstrap/NavDropdown";
import '../stylesheets/Header.css';

class Header extends Component {

  navTo(uri){
    window.location.href = window.location.origin + uri;
  }

  render() {
    return (
      <Navbar bg="light" expand="lg">
          <Navbar.Brand href="/" id="AppHeader">Udacitrivia</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav"/>
          <Navbar.Collapse id="basic-navbar-nav">
          <Nav>
              <Nav.Link id="AppHeaderItem" href='/'>List</Nav.Link>
              <NavDropdown id="AppHeaderItem" title="Add">
                  <NavDropdown.Item id="AppHeaderItem" href='/questions/add'>Add Question</NavDropdown.Item>
                  <NavDropdown.Item id="AppHeaderItem" href='/categories/add'>Add Category</NavDropdown.Item>
              </NavDropdown>
              <Nav.Link id="AppHeaderItem" href='/play'>Play</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Navbar>
    );
  }
}

export default Header;
