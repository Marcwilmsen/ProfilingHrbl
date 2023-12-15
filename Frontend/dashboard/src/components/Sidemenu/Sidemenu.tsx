import { Box, Link, VStack, Image, HStack } from "@chakra-ui/react";
import {
	BsFillHouseDoorFill,
	BsBookshelf,
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
			<Image
				src="/assets/sod3-logo.png"
				height={50}
				rounded="lg"
				objectFit="cover"
				position="absolute"
				inset={5}
				filter="blur(16px)"
				zIndex={0}
				transform="scale(1.1, .9)"
			/>
			<Image
				zIndex={100}
				height={50}
				position="relative"
				src="/assets/sod3-logo.png"
			/>

			<VStack mt={10} spacing={3} align="center" color="black">
				<HStack>
					<BsFillHouseDoorFill />
					<Link href="/page1">Main Dashboard</Link>
				</HStack>
				<HStack>
					<BsBookshelf />
					// Disabled link
					<Link
						href="#"
						color="gray.400"
						_hover={{ textDecoration: "none", color: "gray.400" }}
						pointerEvents="none"
						cursor="default"
					>
						Profiles
					</Link>
				</HStack>
				<HStack>
					<BsGrid1X2Fill />
					// Disabled link
					<Link
						href="#"
						color="gray.400"
						_hover={{ textDecoration: "none", color: "gray.400" }}
						pointerEvents="none"
						cursor="default"
					>
						Zones
					</Link>
				</HStack>
			</VStack>
		</Box>
	);
};

export default Sidemenu;
