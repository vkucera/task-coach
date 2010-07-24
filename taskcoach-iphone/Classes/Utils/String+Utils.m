//
//  String+Utils.m
//  BookBuddy
//
//  Created by Jérôme Laheurte on 26/12/08.
//  Copyright 2008 Jérôme Laheurte. See COPYING for details.
//

#import "String+Utils.h"
#import "i18n.h"

@implementation NSString (Utils)

+ (NSString *)stringFromUTF8Data:(NSData *)data
{
	static unsigned char zero = 0;
	
	// Seems the iPhone doesn't know about kCFStringEncodingUTF8...
	NSMutableData *mdata = [[[NSMutableData alloc] initWithData:data] autorelease];
	[mdata appendBytes:&zero length:1];
	
	return [NSString stringWithUTF8String:[mdata bytes]];
}

// This is *ugly* but I have trouble with Keyed(Un)Archiver

+ (NSString *)decodeData:(NSData *)data
{
	const char *bf = [data bytes];
	NSMutableArray *parts = [[[NSMutableArray alloc] init] autorelease];

	for (NSInteger i = 0; i < [data length]; ++i)
	{
		[parts addObject:[NSString stringWithFormat:@"%02x", (int)((unsigned char *)bf)[i]]];
	}

	return [@"" stringByJoiningStrings:parts];
}

- (NSData *)encoded
{
	NSMutableData *data = [[[NSMutableData alloc] init] autorelease];
	const char *bf = [self UTF8String];

	if (strlen(bf) % 2)
		return nil;

	while (*bf)
	{
		int v;
		if (sscanf((const char*)bf, "%02x", &v) != 1)
			return nil;

		unsigned char c = v;
		[data appendBytes:&c length:1];
		
		bf += 2;
	}

	return data;
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
			
			return [result autorelease];
		}
	}
}

+ (NSString *)formatTimeInterval:(NSInteger)tm
{
	NSMutableArray *comp = [[[NSMutableArray alloc] initWithCapacity:4] autorelease];
	
	[comp addObject:[NSString stringWithFormat:_("%d sec"), tm % 60]];
	tm /= 60;
	if (tm)
	{
		[comp insertObject:[NSString stringWithFormat:_("%d min"), tm % 60] atIndex:0];
		tm /= 60;
		if (tm)
		{
			[comp insertObject:[NSString stringWithFormat:_("%d hours"), tm % 24] atIndex:0];
			tm /= 24;
			if (tm)
			{
				[comp insertObject:[NSString stringWithFormat:_("%d days"), tm] atIndex:0];
			}
		}
	}
	
	return [@", " stringByJoiningStrings:comp];
}

@end
