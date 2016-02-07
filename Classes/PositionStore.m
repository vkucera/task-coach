//
//  PositionStore.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "PositionStore.h"

static PositionStore *_instance = nil;

@implementation Position

@synthesize indexPath;
@synthesize type;
@synthesize searchWord;

- (CGPoint)scrollPosition
{
	static CGPoint p = {0, 0};
	p.y = _scrollPosition;
	return p;
}

- initWithController:(id <RestorableController>)controller indexPath:(NSIndexPath *)path type:(NSInteger)theType searchWord:(NSString *)word
{
	if (self = [super init])
	{
		CGPoint p = [controller tableView].contentOffset;

		_scrollPosition = p.y;
		indexPath = [path retain];
		type = theType;
		if ([word length])
			searchWord = [word copy];
	}
	
	return self;
}

- initWithCoder:(NSCoder *)coder
{
	if (self = [super init])
	{
		_scrollPosition = [coder decodeIntegerForKey:@"scrollPosition"];
		indexPath = [[coder decodeObjectForKey:@"indexPath"] retain];
		type = [coder decodeIntegerForKey:@"type"];
		searchWord = [[coder decodeObjectForKey:@"searchWord"] copy];
	}
	
	return self;
}

- (void)dealloc
{
	[indexPath release];
	[searchWord release];
	
	[super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)coder
{
	[coder encodeInteger:_scrollPosition forKey:@"scrollPosition"];
	[coder encodeObject:indexPath forKey:@"indexPath"];
	[coder encodeInteger:type forKey:@"type"];
	if (searchWord)
		[coder encodeObject:searchWord forKey:@"searchWord"];
}

@end

//============================

@implementation PositionStore

+ (PositionStore *)instance
{
	if (!_instance)
	{
		_instance = [[PositionStore alloc] init];
	}
	
	return _instance;
}

- init
{
	if (self = [super init])
	{
		positions = [[NSMutableArray alloc] initWithCapacity:3];
	}
	
	return self;
}

- initWithFile:(NSString *)path
{
	if (self = [super init])
	{
		NSData *data = [[NSData alloc] initWithContentsOfFile:path];
		positions = [[NSKeyedUnarchiver unarchiveObjectWithData:data] retain];
		[data release];
	}
	
	return self;
}

- (void)save:(NSString *)path
{
	[NSKeyedArchiver archiveRootObject:positions toFile:path];
}


- (void)dealloc
{
	[positions release];
	
	[super dealloc];
}

- (void)push:(id <RestorableController>)controller indexPath:(NSIndexPath *)indexPath type:(NSInteger)theType searchWord:(NSString *)word
{
	Position *pos = [[Position alloc] initWithController:controller indexPath:indexPath type:theType searchWord:word];
	[positions addObject:pos];
	[pos release];
}

- (void)pop
{
	[positions removeLastObject];
}

- (void)restore:(id <RestorableController>)controller
{
	if (current >= [positions count])
		return;

	Position *pos = [positions objectAtIndex:current];
	++current;
	[controller restorePosition:pos store:self];
}

@end