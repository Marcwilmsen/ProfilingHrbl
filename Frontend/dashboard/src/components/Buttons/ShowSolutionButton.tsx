import React from 'react';
import { Button } from '@chakra-ui/react';
import { BsCloudDownloadFill } from 'react-icons/bs';
import { useNavigate } from 'react-router-dom';

interface ShowSolutionButtonProps {
    pagePath: string;
    buttonText: string;
}

const ShowSolutionButton: React.FC<ShowSolutionButtonProps> = ({ pagePath, buttonText }) => {
    const navigate = useNavigate();

    const handleClick = () => {
        navigate(pagePath);
    };

    return (
        <Button
            onClick={handleClick}
            colorScheme="green"
            width="full"
            shadow="md"
            border="none"
            _hover={{
                bg: 'green.500',
                transform: 'translateY(-2px)',
                boxShadow: 'lg',
            }}
            leftIcon={<BsCloudDownloadFill />}
        >
            {buttonText}
        </Button>
    );
};

export default ShowSolutionButton;
