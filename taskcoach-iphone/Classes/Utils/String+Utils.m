//
//  String+Utils.m
//  BookBuddy
//
//  Created by Jérôme Laheurte on 26/12/08.
//  Copyright 2008 Jérôme Laheurte. See COPYING for details.
//

#import "String+Utils.h"

@implementation NSString (Utils)

+ (NSString *)stringFromUTF8Data:(NSData *)data
{
	static unsigned char zero = 0;
	
	// Seems the iPhone doesn't know about kCFStringEncodingUTF8...
	NSMutableData *mdata = [[[NSMutableData alloc] initWithData:data] autorelease];
	[mdata appendBytes:&zero length:1];
	
	return [NSString stringWithUTF8String:[mdata bytes]];
}

- (NSString *)stringByJoiningStrings:(NSArray *)strings
{
	switch ([strings count])
	{
		case 0:
			return @"";
		case 1:
			return [[[strings objectAtIndex:0] copy] autorelease];
		default:
		{
			NSMutableString *result = [[NSMutableString alloc] initWithString:[strings objectAtIndex:0]];
			
			for (NSInteger i = 1; i < [strings count]; ++i)
				[result appendFormat:@"%@%@", self, [strings objectAtIndex:i]];
			
			return result;
		}
	}
}

@end
