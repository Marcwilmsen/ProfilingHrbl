import { Box, VStack, Image, HStack } from "@chakra-ui/react";
import { Link } from "react-router-dom";
import {
	BsFillHouseDoorFill,
	BsGrid1X2Fill,
} from "react-icons/bs";

const Sidemenu: React.FC = () => {
	return (
		<Box
			width="15%"
			backgroundColor="white"
			p={5}
			height="100vh"
			position="fixed"
		>
			<VStack mt={5} mb={5} spacing={3} align="center" color="black">
				<Image height={50} src="/assets/sod3-logo.png" />
				<HStack>
					<BsFillHouseDoorFill />
					<Link to="/">Main Dashboard</Link>
				</HStack>
				<HStack>
					<BsGrid1X2Fill />
					<Link to="/analytics">Analytics</Link>
				</HStack>
				<HStack>
					<BsGrid1X2Fill />
					<Link to="/master-one">Master Area 1</Link>
				</HStack>
				<HStack>
					<BsGrid1X2Fill />
					<Link to="/master-two">Master Area 2</Link>
				</HStack>{" "}
				<HStack>
					<BsGrid1X2Fill />
					<Link to="/master-three">Master Area 3</Link>
				</HStack>
				<HStack>
					<BsGrid1X2Fill />
					<Link to="/master-four">Master Area 4</Link>
				</HStack>
			</VStack>
		</Box>
	);
};

export default Sidemenu;
