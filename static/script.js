// script.js

// Ensure the script runs after the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize WebSocket connection and session management
    class MisinformationBot {
        constructor() {
            this.sessionId = this.getSessionId();
            this.ws = null;
            this.activeCard = null;
            this.initWebSocket();
            this.cacheDOMElements();
            this.bindEvents();
            this.initQuantumEffects();
        }

        // Generate or retrieve session ID
        getSessionId() {
            let sessionId = localStorage.getItem('session_id');
            if (!sessionId) {
                sessionId = this.generateUUID();
                localStorage.setItem('session_id', sessionId);
            }
            return sessionId;
        }

        // Quantum UUID generator using Crypto API
        generateUUID() {
            const array = new Uint8Array(16);
            crypto.getRandomValues(array);
            // Convert to hex and format as UUID
            const hex = Array.from(array, b => b.toString(16).padStart(2, '0')).join('');
            return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-4${hex.slice(13, 16)}-a${hex.slice(17, 20)}-${hex.slice(20, 32)}`;
        }

        // Initialize WebSocket connection
        initWebSocket() {
            this.ws = new WebSocket(`ws://${window.location.hostname}:8000/ws/${this.sessionId}`);
            this.ws.onopen = () => console.log('WebSocket connection opened');
            this.ws.onmessage = (event) => this.handleMessage(event);
            this.ws.onclose = () => console.log('WebSocket connection closed');
        }

        // Cache frequently accessed DOM elements
        cacheDOMElements() {
            this.terminal = document.getElementById('terminal');
            this.reports = document.getElementById('reports');
            this.inputField = document.getElementById('input-field');
            this.sendButton = document.getElementById('send-button');
            this.followupSection = document.getElementById('followup-section');
            this.followupChat = null;
        }

        // Bind event listeners
        bindEvents() {
            this.sendButton.addEventListener('click', () => this.sendMessage());
            this.inputField.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') this.sendMessage();
            });

            // Agent card click events for toggling content display
            const cardTitles = document.querySelectorAll('.card-title');
            cardTitles.forEach(title => {
                title.addEventListener('click', () => {
                    const content = title.parentElement.querySelector('.card-content');
                    content.style.display = content.style.display === 'none' ? 'block' : 'none';
                });
            });
        }

        // Initialize quantum effects (e.g., animations)
        initQuantumEffects() {
            // Use GSAP to animate agent cards with a quantum tunneling effect
            gsap.utils.toArray('.agent-card').forEach(card => {
                gsap.fromTo(card, { opacity: 0, y: 20 }, {
                    opacity: 1,
                    y: 0,
                    duration: 1,
                    ease: 'power3.out',
                    stagger: 0.1,
                    scrollTrigger: {
                        trigger: card,
                        start: 'top 80%',
                        toggleActions: 'play none none none',
                    }
                });
            });
        }

        // Handle incoming WebSocket messages
        handleMessage(event) {
            const messageData = JSON.parse(event.data);

            switch (messageData.type) {
                case 'thinking':
                    this.appendToTerminal(messageData.content, 'thinking');
                    break;
                case 'bot-output':
                    this.appendToTerminal(messageData.content, 'bot-output');
                    break;
                case 'agent_update':
                    this.updateAgentCard(messageData.agent, messageData.content);
                    break;
                case 'final_report':
                    this.displayFinalReport(messageData.content);
                    break;
                case 'followup_response':
                    this.addToFollowupChat(messageData.content, 'bot');
                    break;
                case 'error':
                    this.appendToTerminal(`Error: ${messageData.content}`, 'error');
                    break;
                default:
                    console.warn('Unknown message type:', messageData.type);
            }
        }

        // Append messages to the terminal with appropriate styling
        appendToTerminal(content, type) {
            const line = document.createElement('div');
            line.classList.add('line', type);
            let icon = '';
            switch (type) {
                case 'user-input':
                    icon = '> ';
                    break;
                case 'bot-output':
                    icon = '<i class="fas fa-microchip"></i> ';
                    break;
                case 'thinking':
                    icon = '<i class="fas fa-spinner fa-spin"></i> ';
                    break;
                case 'error':
                    icon = '<i class="fas fa-exclamation-triangle"></i> ';
                    break;
            }
            line.innerHTML = `${icon}${content}`;
            this.terminal.appendChild(line);
            this.terminal.scrollTop = this.terminal.scrollHeight;
        }

        // Send user message to the server
        sendMessage() {
            const message = this.inputField.value.trim();
            if (message !== '') {
                this.appendToTerminal(message, 'user-input');
                this.inputField.value = '';
                this.ws.send(JSON.stringify({ type: 'new_question', content: message }));
            }
        }

        // Update the agent card with new content
        updateAgentCard(agentName, agentData) {
            const cardId = this.getAgentCardId(agentName);
            const card = document.getElementById(cardId);

            if (card) {
                const contentContainer = card.querySelector('.card-content');
                contentContainer.innerHTML = marked.parse(agentData);

                // Activate laser animation
                card.classList.add('active');
                if (this.activeCard && this.activeCard !== cardId) {
                    document.getElementById(this.activeCard).classList.remove('active');
                }
                this.activeCard = cardId;

                // Apply quantum ripple effect using GSAP
                gsap.fromTo(contentContainer, { opacity: 0 }, { opacity: 1, duration: 0.5 });

                // If the Visualization Agent, render the timeline
                if (agentName === 'Visualization Agent') {
                    this.renderTimeline(agentData);
                }
            }
        }

        // Generate card ID from agent name
        getAgentCardId(agentName) {
            return agentName.toLowerCase().replace(/ /g, '-') + '-card';
        }

        // Display the final report and initiate follow-up section
        displayFinalReport(content) {
            const finalFeedbackCard = document.getElementById('feedback-card');
            if (finalFeedbackCard) {
                const contentContainer = finalFeedbackCard.querySelector('.card-content');
                contentContainer.innerHTML = marked.parse(content);
                finalFeedbackCard.classList.add('active');
            }
            this.createFollowupChat();
        }

        // Create follow-up chat section
        createFollowupChat() {
            if (this.followupChat) return; // Prevent multiple initializations

            this.followupSection.style.display = 'block';

            // Chat display area
            this.followupChat = document.createElement('div');
            this.followupChat.id = 'followup-chat';
            this.followupSection.appendChild(this.followupChat);

            // Input area
            const inputArea = document.createElement('div');
            inputArea.id = 'followup-input-area';

            const inputField = document.createElement('input');
            inputField.type = 'text';
            inputField.id = 'followup-input-field';
            inputField.placeholder = 'Ask a follow-up question...';
            inputArea.appendChild(inputField);

            const sendButton = document.createElement('button');
            sendButton.id = 'followup-send-button';
            sendButton.textContent = 'Send';
            sendButton.addEventListener('click', () => this.sendFollowupQuestion());
            inputArea.appendChild(sendButton);

            inputField.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') this.sendFollowupQuestion();
            });

            this.followupSection.appendChild(inputArea);
        }

        // Send follow-up question to the server
        sendFollowupQuestion() {
            const inputField = document.getElementById('followup-input-field');
            const message = inputField.value.trim();
            if (message !== '') {
                this.addToFollowupChat(message, 'user');
                inputField.value = '';
                this.ws.send(JSON.stringify({ type: 'followup', content: message }));
            }
        }

        // Add messages to the follow-up chat area
        addToFollowupChat(message, sender) {
            const line = document.createElement('div');
            line.classList.add('line', sender === 'user' ? 'user-input' : 'bot-output');
            line.innerHTML = sender === 'user' ? `> ${message}` : `<i class="fas fa-microchip"></i> ${message}`;
            this.followupChat.appendChild(line);
            this.followupChat.scrollTop = this.followupChat.scrollHeight;
        }

        // Render the timeline visualization using D3.js
        renderTimeline(agentData) {
            // Extract timeline data from agentData
            const timelineData = this.extractTimelineData(agentData);
            if (!timelineData) return;

            // Remove any existing SVG
            d3.select('#timeline-container').selectAll('*').remove();

            const margin = { top: 20, right: 20, bottom: 30, left: 50 };
            const width = document.getElementById('timeline-container').offsetWidth - margin.left - margin.right;
            const height = 300 - margin.top - margin.bottom;

            const svg = d3.select('#timeline-container')
                .append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom)
                .append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);

            // Parse dates and set up scales
            const parseDate = d3.timeParse('%Y-%m-%d');
            timelineData.forEach(d => {
                d.date = parseDate(d.date) || new Date();
            });

            const xScale = d3.scaleTime()
                .domain(d3.extent(timelineData, d => d.date))
                .range([0, width]);

            const yScale = d3.scaleLinear()
                .domain([0, 1])
                .range([height / 2, height / 2]); // Fixed y position

            // Add timeline line
            svg.append('line')
                .attr('class', 'timeline-line')
                .attr('x1', 0)
                .attr('y1', height / 2)
                .attr('x2', width)
                .attr('y2', height / 2);

            // Add circles for events
            svg.selectAll('circle')
                .data(timelineData)
                .enter()
                .append('circle')
                .attr('class', 'timeline-circle')
                .attr('cx', d => xScale(d.date))
                .attr('cy', height / 2)
                .attr('r', 6)
                .attr('fill', d => this.getEventColor(d.type))
                .on('mouseover', (event, d) => this.showTooltip(event, d.title))
                .on('mouseout', () => this.hideTooltip());

            // Add X-axis
            svg.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(xScale));

            // Initialize tooltip
            this.tooltip = d3.select('body').append('div')
                .attr('class', 'tooltip')
                .style('opacity', 0);
        }

        // Extract timeline data from agentData content
        extractTimelineData(content) {
            // Assume the content is JSON with an 'events' array
            try {
                const data = JSON.parse(content);
                return data.events || null;
            } catch (error) {
                console.error('Error parsing timeline data:', error);
                return null;
            }
        }

        // Get color based on event type
        getEventColor(type) {
            switch (type) {
                case 'claim': return '#00ff41';
                case 'subclaim': return '#1e90ff';
                case 'question': return '#ffae00';
                case 'result': return '#ff4500';
                case 'analysis': return '#ff1493';
                default: return '#cccccc';
            }
        }

        // Show tooltip on hover
        showTooltip(event, text) {
            this.tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            this.tooltip.html(text)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 28) + 'px');
        }

        // Hide tooltip
        hideTooltip() {
            this.tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        }
    }

    // Instantiate the bot
    const bot = new MisinformationBot();
});
