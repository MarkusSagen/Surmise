import React, { Component } from 'react'
import Navbar from "./Navbar"
import FileUpload from "./FileUpload"
import TextUpload from './TextUpload'
import Card from "./Card"
import ProjectMember from "./ProjectMember"

const defaultProfile = require("./img/default.jpg");
const markusProfile = require("./img/Markus_profile.jpeg");
const sebbeProfile = require("./img/Sebastian_profile.jpg");
const nilsProfile = require("./img/Nils_profile.jpg");
const alexProfile = require("./img/Alexander_profile.jpg");

const askQuestionIcon = require("./img/stock/Ask-Question.svg");
const contactIcon = require("./img/stock/Contact.svg");
const doneIcon = require("./img/stock/Done.svg");
const FAQIcon = require("./img/stock/FAQ.svg");
const QAIcon = require("./img/stock/QA.svg");
const QuestionsIcon = require("./img/stock/Questions.svg");
const SiteIcon = require("./img/stock/Site-Running.svg");


class LandingPage extends Component {
    state = {
        isFetching: false,
        files: [],
        err: "",
    }

    handleTextUpload = (text, mode) => {
        this.changeState()
        const body = { text: text, user: this.props.user, new: false }
        if (this.props.isAuthed) {
            fetch(`/textUpload`, {
                method: 'post',
                headers: {
                    "Authorization": this.props.user,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(body)
            }).then(resp => resp.json()).then(data => {

                console.log(data);
                this.changeState();
                this.props.history.push({
                    pathname: `/files/${this.props.user}`,
                    state: { mode: mode },
                });
            })
        }
    }

    handleFileUpload = (url, file, mode) => {
        this.setState({ isFetching: true })
        file.append("new", false)
        console.log("WHAY?")
        if (this.props.isAuthed) {
            fetch(`/${url}`, {
                method: 'post',
                headers: {
                    "Authorization": this.props.user
                },
                body: file
            }).then(resp => resp.json()).then(data => {

                console.log(data);
                this.changeState();
                this.props.history.push({
                    pathname: `/files/${this.props.user}`,
                    state: { mode: mode },
                });
            })
        }
    }

    changeState = () => {
        this.setState({ isFetching: !this.state.isFetching })
    }

    putFile = (f) => {
        const arr = [];
        for (let i = 0; i < f.length; i++) {
            arr.push(f[i].name)
        }
        this.setState({ files: arr });
    }
    setError = (text) => {
        this.setState({ err: text })
        setTimeout(() => {
            this.setState({ err: "" })
        }, 2000)
    }
    render() {
        return (
            <header>
                <Navbar />
                <div className="landing-main-content">
                    <div className="main-container">
                        <div className="jumbotron">
                            <div className="title">
                                <h1>Surmize</h1>
                                <p>Upload your Documents or Text and gain quick insight</p>
                            </div>
                            <div className="upload-section">
                                <FileUpload setError={this.setError} err={this.state.err} putFile={this.putFile} sendFile={this.handleFileUpload} />
                                <TextUpload uploadText={this.handleTextUpload} />
                            </div>
                        </div>
                    </div>
                </div>
                <div className="how-section">
                    <div className="main-container">
                        <h1>How To Use</h1>
                        <div className="card-container">
                            <Card
                                title="Upload Files"
                                imgSrc={QAIcon}
                            />
                            <Card
                                title="Ask Questions"
                                imgSrc={FAQIcon}
                            />
                            <Card
                                title="Save Results"
                                imgSrc={doneIcon}
                            />
                        </div>
                    </div>
                </div>
                <div className="about">
                    <div className="about-title">
                        <h1>About Us</h1>
                    </div>
                    <div className="about-main">
                        <div className="main-container">
                            <div className="about-content">
                                <div>
                                    <h6>Lorem Ipsum Parabellum</h6>
                                    <p> Lorem ipsum dolor sit amet consectetur adipisicing elit. Itaque repellat magnam facilis doloribus. Esse quasi accusamus eveniet rem adipisci dolore, porro quia reprehenderit temporibus, perferendis tempora repellendus, obcaecati libero hic similique. Aliquam
                                    praesentium modi possimus, at omnis obcaecati, totam sunt soluta id iure molestiae excepturi consequatur quia? Excepturi, at voluptas.
                                    </p>
                                </div>
                                <div className="about-pics">
                                    <ProjectMember
                                        src={markusProfile}
                                        firstName="Markus"
                                        lastName="Sagen"
                                        imgWidth="50px"
                                        imgHeight="50px"
                                        linkedInLink="https://linkedin.com/MarkusSagen"
                                        githubLink="https://github.com/MarkusSagen"
                                    />
                                    <ProjectMember
                                        src={sebbeProfile}
                                        firstName="Sebastian"
                                        lastName="Rollino"
                                        imgWidth="50px"
                                        imgHeight="50px"
                                        linkedInLink="https://www.linkedin.com/in/sebastian-rollino-4019b8183/"
                                        githubLink="https://github.com/sebbersk"
                                    />
                                    <ProjectMember
                                        src={nilsProfile}
                                        firstName="Nils"
                                        lastName="Hedberg"
                                        imgWidth="50px"
                                        imgHeight="50px"
                                        linkedInLink="https://www.linkedin.com/in/nils-hedberg-2784a8152/"
                                        githubLink="https://github.com/nilshugo"
                                    />
                                    <ProjectMember
                                        src={alexProfile}
                                        firstName="Alexander"
                                        lastName="Bergkvist"
                                        imgWidth="50px"
                                        imgHeight="50px"
                                        linkedInLink="https://www.linkedin.com/in/alexander-bergkvist-b79325181/"
                                        githubLink="https://github.com/AlexanderBergkvist"
                                    />
                                </div>
                            </div>
                        </div>

                    </div>
                    <div className="footer"></div>
                </div>



            </header>


        )
    }
}
export default LandingPage;