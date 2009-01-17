//
//  String+Utils.m
//  BookBuddy
//
//  Created by Jérôme Laheurte on 26/12/08.
//  Copyright 2008 __MyCompanyName__. All rights reserved.
//

#import "String+Utils.h"

@implementation NSString (Utils)

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
