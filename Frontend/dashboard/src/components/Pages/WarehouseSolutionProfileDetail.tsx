import React, { useEffect, useState } from "react";
import {
  Box,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Stat,
  StatLabel,
  StatNumber,
  StatGroup,
  Heading
} from "@chakra-ui/react";
import { useParams } from "react-router-dom";
import config from '../../config';
import { format, parseISO } from 'date-fns';


interface WarehouseSolutionProfileDetail {
    sku_id: number;
    solution_location: string;
    masterlist_location: string;
}

interface StartData {
    number_of_generations: number;
    algo_from_date: string;
    algo_too_date: string;
    percentage_to_stop: string;
    day_where_algo_was_started: string;
    // Other fields as needed
}

const WarehouseSolutionProfileDetailsPage: React.FC = () => {
    const [profileDetails, setProfileDetails] = useState<WarehouseSolutionProfileDetail[]>([]);
    const [startData, setStartData] = useState<StartData | null>(null);
    const [error, setError] = useState<string | null>(null);
    const { id } = useParams<{ id: string }>();

    useEffect(() => {      
        fetch(`${config.BASE_URL}warehouse-solution-profiles/${id}/`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                setProfileDetails(data.assignments);
                console.log(data)
                setStartData(data.start_data);
            })
            .catch((error) => {
                console.error("There was a problem with the fetch operation:", error);
                setError(error.message);
            });
    }, [id]);

    const handleDownload = () => {
        window.location.href = `${config.BASE_URL}download/solution_profile/${id}/`;
    };

    if (error) {
        return <Box width="80%" position="absolute" top="0" right="10" mt={5}><div>Error: {error}</div></Box>;
    }

    if (!profileDetails.length) {
        return <Box width="80%" position="absolute" top="0" right="10" mt={5}><div>Loading...</div></Box>;
    }

    // Function to round the time to the nearest minute and format it
    const roundToNearestMinute = (timeString: string) => {
        const date = parseISO(timeString);
        return format(date, "do MMM yyyy, HH:mm"); // e.g., "12th Mar 2024, 15:30"
    };

    return (
        <Box width="80%" position="absolute" top="0" right="10" mt={5}>
            <Button colorScheme="blue" onClick={handleDownload} mb={4}>
                Download Solution as Masterlist Excel
            </Button>

            {startData && (
                <Box mb={4} p={4} boxShadow="md" borderRadius="lg" bg="white">
                    <Heading size="md" mb={4}>PyGAD Algo Start Details</Heading>
                    <StatGroup>
                        <Stat>
                            <StatLabel>Generations</StatLabel>
                            <StatNumber>{startData.number_of_generations}</StatNumber>
                        </Stat>
                        <Stat>
                            <StatLabel>Stop At %</StatLabel>
                            <StatNumber>{startData.percentage_to_stop}</StatNumber>
                        </Stat>
                        <Stat>
                            <StatLabel>From</StatLabel>
                            <StatNumber>{startData.algo_from_date}</StatNumber>
                        </Stat>
                        <Stat>
                            <StatLabel>To</StatLabel>
                            <StatNumber>{startData.algo_too_date}</StatNumber>
                        </Stat>
                        <Stat>
                            <StatLabel>Started</StatLabel>
                            <StatNumber>{roundToNearestMinute(startData.day_where_algo_was_started)}</StatNumber>
                        </Stat>
                    </StatGroup>
                </Box>
            )}


            <Table variant="simple" colorScheme="teal">
                <Thead>
                    <Tr>
                        <Th>SKU</Th>
                        <Th>Masterlist Location</Th>
                        <Th>Solution Location</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {profileDetails.map((detail, index) => (
                        <Tr key={index} bg={detail.solution_location !== detail.masterlist_location ? "gray.200" : "white"}>
                            <Td>{detail.sku_id}</Td>
                            <Td>{detail.masterlist_location}</Td>
                            <Td>{detail.solution_location}</Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        </Box>
    );
};

export default WarehouseSolutionProfileDetailsPage;
