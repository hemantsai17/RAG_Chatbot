import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import {
    Button, Snackbar, Alert, CircularProgress, Grid,
    List, ListItem, ListItemText, IconButton, Typography, TextField,
    Drawer, Divider, Box, Toolbar, Fab, Tooltip
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import SendIcon from "@mui/icons-material/Send";
import DeleteIcon from "@mui/icons-material/Delete";
import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";
import DOMPurify from "dompurify";
import BookIcon from "@mui/icons-material/MenuBook";
import CommentsDisabledIcon from '@mui/icons-material/CommentsDisabled';
import ClearAllIcon from "@mui/icons-material/ClearAll"; // Clear Chat Icon
import { keyframes } from "@mui/system";
import { fontFamily } from "@mui/system";

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [loading, setLoading] = useState(false);
    const [popup, setPopup] = useState({ open: false, message: "", status: "success" });
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const chatContainerRef = useRef(null);

    useEffect(() => {
        chatContainerRef.current?.scrollTo({ top: chatContainerRef.current.scrollHeight, behavior: "smooth" });
    }, [messages]);

    const clearChat = () => {
        setMessages([]);
    };

    const flicker = keyframes`
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
        `;

    const uploadFiles = async () => {
        if (files.length === 0) return;

        setUploading(true);

        const formData = new FormData();
        files.forEach((file) => {
            formData.append("files", file);
        });

        try {
            const response = await axios.post("https://ragchatbotbackend-231317849456.asia-south1.run.app/uploadDocs", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            console.log("Upload Success:", response.data);
            setPopup({ open: true, message: "Files uploaded successfully!", status: "success" });
            setFiles([]); // Clear uploaded files list
        } catch (error) {
            console.error("Upload Error:", error);
            setPopup({ open: true, message: "Failed to upload files.", status: "error" });
        } finally {
            setUploading(false);
        }
    };

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { text: input, sender: "user" };
        setMessages((prevMessages) => [...prevMessages, userMessage]);
        setInput("");
        setLoading(true);

        let botMessageIndex;



        setMessages((prevMessages) => {
            const newMessages = [
                ...prevMessages,
                {
                    text: (
                        <>
                            <CircularProgress size="0.8em" sx={{ marginRight: "5px" }} />
                            <Typography
                                component="span"
                                sx={{ animation: `${flicker} 1.5s infinite ease-in-out` }}
                            >
                                Thinking...
                            </Typography>
                        </>
                    ),
                    sender: "bot"
                }
            ];
            botMessageIndex = newMessages.length - 1;
            return newMessages;
        });



        try {
            const response = await fetch(`https://ragchatbotbackend-231317849456.asia-south1.run.app/getText?text=${encodeURIComponent(input)}`);
            if (!response.ok || !response.body) throw new Error("Failed to fetch response");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let botReply = "";
            let firstChunk = true;

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                botReply += chunk;

                setMessages((prevMessages) => {
                    const updatedMessages = [...prevMessages];
                    if (firstChunk) {
                        updatedMessages[botMessageIndex] = { text: chunk, sender: "bot" };
                        firstChunk = false;
                    } else {
                        updatedMessages[botMessageIndex].text = botReply;
                    }
                    return updatedMessages;
                });
            }

            setPopup({ open: true, message: "Bot has responded!", status: "success" });
        } catch (error) {
            console.error("Error fetching response:", error);
            setMessages((prevMessages) => {
                const updatedMessages = [...prevMessages];
                updatedMessages[botMessageIndex] = { text: "⚠️ Error fetching response.", sender: "bot" };
                return updatedMessages;
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ display: "flex", height: "100vh" }}>
            {/* Sidebar */}
            <Drawer
                variant="persistent"
                anchor="left"
                open={sidebarOpen}
                sx={{
                    width: sidebarOpen ? 280 : 0,
                    transition: "width 0.3s",
                    flexShrink: 0,
                    "& .MuiDrawer-paper": {
                        width: 280,
                        boxSizing: "border-box",
                        overflowY: "auto",
                        maxHeight: "100vh",
                    },
                }}
            >
                <Toolbar>
                    <IconButton onClick={() => setSidebarOpen(false)}>
                        <CloseIcon />
                    </IconButton>
                </Toolbar>
                <Divider />

                {/* File Upload Section */}
                <Box
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        height: "100%",
                        maxHeight: "calc(100vh - 100px)", // Adjust based on layout
                        overflow: "hidden",
                        padding: 2
                    }}
                >
                    <input
                        type="file"
                        accept="application/pdf"
                        multiple
                        onChange={(e) => setFiles([...files, ...Array.from(e.target.files)])}
                        id="file-upload"
                        hidden
                    />
                    <label htmlFor="file-upload">
                        <Button
                            component="span"
                            variant="contained"
                            startIcon={<CloudUploadIcon />}
                            fullWidth
                        >
                            Upload PDFs
                        </Button>
                    </label>

                    <Divider sx={{ marginY: 2 }} />

                    {/* File List - Responsive Scrollable Area */}
                    <Box sx={{ flexGrow: 1, overflowY: "auto", minHeight: 0 }}>
                        <List>
                            {files.map((file, index) => (
                                <ListItem key={index}
                                    secondaryAction={
                                        <IconButton
                                            edge="end"
                                            color="error"
                                            onClick={() => setFiles(files.filter((_, i) => i !== index))}
                                        >
                                            <DeleteIcon />
                                        </IconButton>
                                    }
                                >
                                    <ListItemText
                                        primary={file.name}
                                        sx={{
                                            whiteSpace: "nowrap",
                                            overflow: "hidden",
                                            textOverflow: "ellipsis",
                                            maxWidth: "200px"
                                        }}
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </Box>

                    {/* Action Buttons */}
                    <Button
                        variant="contained"
                        color="primary"
                        fullWidth
                        onClick={uploadFiles}
                        disabled={uploading || files.length === 0}
                        sx={{ marginTop: 2 }}
                    >
                        {uploading ? <CircularProgress size={24} /> : "Submit"}
                    </Button>
                    <Button
                        variant="contained"
                        color="error"
                        fullWidth
                        onClick={() => setFiles([])}
                        sx={{ marginTop: 1 }}
                    >
                        Clear Docs
                    </Button>
                </Box>

            </Drawer>

            {/* Sidebar Toggle Button (Visible when Sidebar is Collapsed) */}
            {!sidebarOpen && (
                <Fab
                    color="primary"
                    size="small"
                    onClick={() => setSidebarOpen(true)}
                    sx={{
                        position: "absolute",
                        top: 16,
                        left: 16,
                        zIndex: 1500,
                    }}
                >
                    <MenuIcon />
                </Fab>
            )}

            {/* Main Chat Section */}
            <Box sx={{
                flexGrow: 1,
                marginLeft: sidebarOpen ? "0px" : "0px",
                transition: "margin 0.3s",
                display: "flex",
                flexDirection: "column",
                width: sidebarOpen ? "calc(100% - 280px)" : "100%", // Expand chat area
            }}>
                <Grid container alignItems="center" sx={{ padding: 2, width: "100%" }}>
                    {/* Left Spacer - Pushes Title to Center */}
                    <Grid item xs />

                    {/* Center Title */}
                    <Grid item>
                        <Typography variant="h5" fontWeight="bold">UPSChatbot</Typography>
                    </Grid>

                    {/* Right Clear Chat Button */}
                    <Grid item xs display="flex" justifyContent="flex-end">
                        <Tooltip title="Clear Chat">
                            <IconButton color="inherit" onClick={clearChat}>
                                <CommentsDisabledIcon />
                            </IconButton>
                        </Tooltip>
                    </Grid>
                </Grid>

                {!messages.length>0  ? (<Box textAlign="center" mt={4} sx={{

                    flexGrow: 1, overflowY: "auto", padding: "1em"
                }}>
                    {/* Main Heading with Book Icon */}
                    <Box
                        
                        sx={{
                            border: "2px #ccc", // Light grey border
                            borderRadius: "12px", // Rounded corners
                            backgroundColor: "#EEEEEE", // Light grey background
                            maxWidth: "600px", // Limit width
                            margin: "auto", // Center horizontally
                            boxShadow: 2, // Light shadow effect
                        }}>
                        <Typography variant="h3" fontWeight="bold">
                            <BookIcon fontSize="large" sx={{ verticalAlign: "middle", mr: 1 }} />
                            Welcome to UPSChatbot
                        </Typography>

                        {/* Subheading */}
                        <Typography variant="h5" color="textSecondary" mt={1}>
                            Ask Questions Related to UPSC and General Knowledge
                        </Typography>
                    </Box>

                </Box>) :
                    (
                        <div ref={chatContainerRef} style={{ flexGrow: 1, overflowY: "auto", padding: "10px" }}>
                            {messages.map((msg, index) => (
                                <div key={index} style={{
                                    display: "flex",
                                    justifyContent: msg.sender === "user" ? "flex-start" : "flex-end",
                                    marginBottom: "1em"
                                }}>
                                    <div style={{
                                        maxWidth: "100%",
                                        padding: "0em 1em 0em 1em",
                                        borderRadius: msg.sender === "user" ? "1em" : null,
                                        backgroundColor: msg.sender === "user" ? "#EEEEEE" : null,
                                        textAlign: "left", // Ensures text inside is always left-aligned
                                        wordWrap: "break-word",
                                        fontFamily: "system-ui",
                                        fontWeight: 500 /* Slightly bold */
                                    }}>
                                        {typeof msg.text === "string" ? <ReactMarkdown>{DOMPurify.sanitize(msg.text)}</ReactMarkdown> : msg.text}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                {/* Input Field */}
                <Box sx={{ display: "flex", alignItems: "center", padding: 2, borderTop: "1px solid #ddd", backgroundColor: "#fff" }}>
                    <TextField
                        fullWidth
                        variant="outlined"
                        placeholder="Ask your question...😊"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                sendMessage();
                            }
                        }}
                        InputProps={{
                            sx: {
                                borderRadius: "20px", // Adjust border radius
                                backgroundColor: "#fff", // Optional: Add background color
                            },
                        }}
                    />

                    <IconButton color="primary" onClick={sendMessage} disabled={!input.trim()}>
                        <SendIcon />
                    </IconButton>
                </Box>

            </Box>
            <Snackbar open={popup.open} autoHideDuration={3000} onClose={() => setPopup({ ...popup, open: false })}>
                <Alert severity={popup.status}>{popup.message}</Alert>
            </Snackbar>
        </div>
    );
};

export default Chatbot;
