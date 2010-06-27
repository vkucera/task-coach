//
//  ItemParser.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/08/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "ItemParser.h"

@implementation ItemParser

- init
{
	if ((self = [super init]))
	{
		stack = [[NSMutableArray alloc] init];
	}
	
	return self;
}

- (void)dealloc
{
	[current release];
	[stack release];
	
	[super dealloc];
}

- (BaseItem *)parse:(const char *)format
{
	if (format[0] == '[')
	{
		int newLen = strlen(format) - 2;
		char *newFormat = (char *)malloc(newLen + 1);
		
		memcpy(newFormat, format + 1, newLen);
		newFormat[newLen] = 0;
		
		BaseItem *item = [self parse:newFormat];
		
		free(newFormat);
		
		return [[[ListItem alloc] initWithItem:item] autorelease];
	}

	current = [[CompositeItem alloc] initWithItems:[NSArray arrayWithObjects:nil]];
	count = -1;
	
	for (int i = 0; i < strlen(format); ++i)
	{
		switch (format[i])
		{
			case '[':
			{
				BaseItem *item = [[ListItem alloc] initWithItem:[[[CompositeItem alloc] initWithItems:[NSArray arrayWithObjects:nil]] autorelease]];
				[stack addObject:current];
				[current performSelector:@selector(append:) withObject:item];
				[current release];
				current = item;
				
				break;
			}
			case ']':
				[current release];
				current = [[stack lastObject] retain];
				[stack removeLastObject];
				
				break;
			case 'i':
				[current performSelector:@selector(append:) withObject:[[[IntegerItem alloc] init] autorelease]];
				break;
			case 's':
				[current performSelector:@selector(append:) withObject:[[[StringItem alloc] init] autorelease]];
				break;
			case 'z':
				[current performSelector:@selector(append:) withObject:[[[FixedSizeStringItem alloc] init] autorelease]];
				break;
			case 'b':
				if (count == -1)
					break;
				
				[current performSelector:@selector(append:) withObject:[[[DataItem alloc] initWithCount:count] autorelease]];
				count = -1;
				break;
			case 'd':
				[current performSelector:@selector(append:) withObject:[[[VariableDataItem alloc] init] autorelease]];
				break;
			case 't':
				[current performSelector:@selector(append:) withObject:[[[DateItem alloc] init] autorelease]];
				break;
			case '0':
			case '1':
			case '2':
			case '3':
			case '4':
			case '5':
			case '6':
			case '7':
			case '8':
			case '9':
				if (count == -1)
					count = format[i] - '0';
				else
				{
					count *= 10;
					count += format[i] - '0';
				}
				break;
			default:
				break;
		}
	}
	
	BaseItem *ret = [current autorelease];
	current = nil;
	
	[stack removeAllObjects];
	
	return ret;
}

@end
