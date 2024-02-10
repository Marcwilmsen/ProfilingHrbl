import React from 'react';
import { Box, Card, Flex, Grid, GridItem, HStack } from '@chakra-ui/react';
import InputFileButton from '../Input/InputFileButton';
import DownloadButton from '../Buttons/DownloadButton';
import RunAlgorithmForm from '../Forms/RunAlgoForm';
import GrafanaDashboard from '../Dashboards/MainDashboard';
import ConsolePage from './ConsoleComponent'; // Import the ConsolePage component
import config from '../../config';

const Dashboard: React.FC = () => {
    return (
        <>
            <Box width="80%" position="absolute" top="0" right="10" mt={5}>
                <Grid templateColumns="repeat(12, 1fr)" gap={4} alignItems="stretch">
                    {/* RunAlgorithmForm and ConsolePage */}
                    <GridItem colSpan={6}>
                        <Card bg="white" p={3} m={1} h="100%" w="100%">
                            <Flex direction="column" h="100%" w="100%">
                                <RunAlgorithmForm />
                            </Flex>
                        </Card>
                    </GridItem>
                    <GridItem colSpan={6}>
                        <ConsolePage />
                    </GridItem>

                    {/* Upload Buttons */}
                    <GridItem colSpan={12}>
                        <Card bg="white" p={3} m={0} h="auto" w="100%">
                            <HStack spacing={4} justifyContent="flex-start">
                                <InputFileButton
                                    uploadUrl={`${config.BASE_URL}upload/pickdata/`}
                                    acceptedFiles={'.txt'}
                                    label={'Upload Pickdata .txt'}
                                />
                                <InputFileButton
                                    uploadUrl={`${config.BASE_URL}upload/location_matrix/`}
                                    acceptedFiles={'.csv'}
                                    label={'Upload Location Matrix .CSV'}
                                />
                                <InputFileButton
                                    uploadUrl={`${config.BASE_URL}upload/new_masterlist/`}
                                    acceptedFiles={'.xlsx'}
                                    label={'Upload Masterlist .XLSX'}
                                />
                            </HStack>
                        </Card>
                    </GridItem>
                    
                    {/* Download Buttons */}
                    <GridItem colSpan={12}>
                        <Card bg="white" p={3} m={0} h="auto" w="100%">
                            <HStack spacing={4} justifyContent="flex-start">
                                <DownloadButton
                                    width="full"
                                    downloadPath={`${config.BASE_URL}download/pickdata/`}
                                    fileName={'pickdata.txt'}
                                    buttonText={'Download Pickdata from DB'}
                                />
                                <DownloadButton
                                    width="full"
                                    downloadPath={`${config.BASE_URL}download/masterlist_profile/`}
                                    fileName={'new_masterlist.xlsx'}
                                    buttonText={'Download Masterlist from DB'}
                                />
                            </HStack>
                        </Card>
                    </GridItem>
                </Grid>
                
                <GrafanaDashboard  />
            </Box>
        </>
    );
};

export default Dashboard;
