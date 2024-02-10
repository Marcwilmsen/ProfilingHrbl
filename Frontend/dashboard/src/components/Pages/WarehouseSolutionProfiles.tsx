import React, { useEffect, useState } from "react";
import { Box, Button } from "@chakra-ui/react";
import { useNavigate } from 'react-router-dom';
import config from '../../config';

interface WarehouseSolutionProfile {
    id: number;
    name: string;
    timestamp: string;
}

const WarehouseSolutionProfilesPage: React.FC = () => {
    const [profiles, setProfiles] = useState<WarehouseSolutionProfile[]>([]);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetch(`${config.BASE_URL}warehouse-solution-profiles/`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                // Sort profiles by ID in descending order
                const sortedProfiles = data.sort((a: WarehouseSolutionProfile, b: WarehouseSolutionProfile) => b.id - a.id);
                setProfiles(sortedProfiles);
            })
            .catch((error) => {
                console.error("There was a problem with the fetch operation:", error);
                setError(error.message);
            });
    }, []);

    const viewProfileDetails = (profileId: number) => {
        navigate(`/warehouse-solution-profiles/${profileId}`);
    };

    if (error) {
        return (
            <Box width="80%" position="absolute" top="0" right="10" mt={5}>
                <div>Error: {error}</div>
            </Box>
        );
    }

    return (
        <Box width="80%" position="absolute" top="0" right="10" mt={5}>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Timestamp</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {profiles.map((profile) => (
                        <tr key={profile.id}>
                            <td>{profile.id}</td>
                            <td>{profile.name}</td>
                            <td>{profile.timestamp}</td>
                            <td>
                                <Button colorScheme="blue" onClick={() => viewProfileDetails(profile.id)}>
                                    View
                                </Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </Box>
    );
};

export default WarehouseSolutionProfilesPage;
