// ConsolePage.tsx
import React, { useState, useEffect, useRef } from 'react';
import { Box, Card, Textarea, Switch, Flex, FormLabel } from '@chakra-ui/react';
import config from '../../config';

const ConsolePage: React.FC = () => {
    const [logs, setLogs] = useState<string>('');
    const consoleRef = useRef<HTMLTextAreaElement>(null);
    const [autoScroll, setAutoScroll] = useState(true);
    let socket: WebSocket | null = null;

    useEffect(() => {
        socket = new WebSocket(`${config.SOCKET_URL}ws/console/`);

        socket.onmessage = event => {
            const data = event.data;
            setLogs(prevLogs => prevLogs + '\n' + data);

            if (autoScroll && consoleRef.current) {
                consoleRef.current.scrollTop = consoleRef.current.scrollHeight - consoleRef.current.clientHeight;
            }
        };

        socket.onerror = error => {
            console.error("WebSocket error observed:", error);
        };

        return () => {
            if (socket) {
                socket.close();
            }
        };
    }, [autoScroll]);

    const handleAutoScrollToggle = () => {
        setAutoScroll(!autoScroll);
    };

    return (
        <Card bg="white" p={1} m={1} h="calc(100% - 0rem)" w="100%">
            <Flex justifyContent="space-between" alignItems="center">
                <FormLabel htmlFor="auto-scroll" mb="0" fontSize="sm">
                    Auto-Scroll to Latest
                </FormLabel>
                <Switch id="auto-scroll" isChecked={autoScroll} onChange={handleAutoScrollToggle} size="sm" />
                <Box flexGrow={1} textAlign="right" fontSize="m">
                    Output Console:
                </Box>
            </Flex>
            <Textarea
                ref={consoleRef}
                value={logs}
                readOnly
                style={{ width: '100%', height: 'calc(100% - 1.5rem)', resize: 'none', fontSize: 'smaller', overflowY: 'auto', padding: 0 }} // Adjust styling here
            />
        </Card>
    );
};

export default ConsolePage;
