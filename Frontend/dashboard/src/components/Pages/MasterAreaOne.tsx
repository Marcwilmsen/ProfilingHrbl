import { Box } from "@chakra-ui/react";

const MasterAreaOne: React.FC = () => {
	return (
		<>
			<Box width="80%" position="absolute" top="0" right="10" mt={5}>
				<iframe
					src="https://grafana.sod3.eu/public-dashboards/23fcaf86bb6646e2be48b30eee53ff8a"
					width="100%"
					height="1200"
					title="Grafana Dashboard"
				></iframe>
			</Box>
		</>
	);
};

export default MasterAreaOne;
