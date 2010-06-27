//
//  Configuration.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"
#import "Configuration.h"
#import "CDFile.h"

static Configuration *_configuration = NULL;

@implementation Configuration

@synthesize showCompleted;
@synthesize showInactive;
@synthesize iconPosition;
@synthesize compactTasks;
@synthesize confirmComplete;
@synthesize soonDays;
@synthesize name;
@synthesize domain;
@synthesize viewStyle;
@synthesize taskGrouping;
@synthesize reverseGrouping;

+ (Configuration *)configuration
{
	if (!_configuration)
		_configuration = [[Configuration alloc] init];
	return _configuration;
}

- init
{
	if ((self = [super init]))
	{
		NSUserDefaults *config = [NSUserDefaults standardUserDefaults];

		showCompleted = [config boolForKey:@"showcompleted"];
		if ([config objectForKey:@"showinactive"])
			showInactive = [config boolForKey:@"showinactive"];
		else
			showInactive = YES;
		iconPosition = [config integerForKey:@"iconposition"];
		compactTasks = [config boolForKey:@"compacttasks"];
		confirmComplete = [config boolForKey:@"confirmcomplete"];
		soonDays = [config integerForKey:@"soondays"];
		
		if (!soonDays)
			soonDays = 1;
		
		NSLog(@"Soon days: %d", soonDays);

		name = [[config stringForKey:@"name"] copy];
		domain = [[config stringForKey:@"domain"] copy];

		viewStyle = [config integerForKey:@"viewStyle"];
		
		if ([config objectForKey:@"taskGrouping"])
		{
			taskGrouping = [config integerForKey:@"taskGrouping"];
			reverseGrouping = [config integerForKey:@"reverseGrouping"];
		}
		else
		{
			taskGrouping = GROUP_STATUS;
			reverseGrouping = NO;
		}

		NSString *guid = [config stringForKey:@"currentfile"];
		if (guid)
		{
			currentFileGuid = [guid copy];
		}
	}
	
	return self;
}

- (void)dealloc
{
	[name release];
	[domain release];
	[currentFileGuid release];

	[super dealloc];
}

- (void)save
{
	NSUserDefaults *config = [NSUserDefaults standardUserDefaults];

	// Save only read-write properties
	if (name)
		[config setObject:name forKey:@"name"];
	if (domain)
		[config setObject:domain forKey:@"domain"];
	
	[config setInteger:viewStyle forKey:@"viewStyle"];
	[config setInteger:taskGrouping forKey:@"taskGrouping"];
	[config setInteger:reverseGrouping forKey:@"reverseGrouping"];

	if (currentFileGuid)
	{
		[config setObject:currentFileGuid forKey:@"currentfile"];
	}

	[config synchronize];
}

#pragma mark -
#pragma mark CoreData stuff

- (NSInteger)cdFileCount
{
	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDFile" inManagedObjectContext:getManagedObjectContext()]];
	NSError *error;
	NSInteger count;
	if ((count = [getManagedObjectContext() countForFetchRequest:request error:&error]) < 0)
	{
		NSLog(@"Could not get file count: %@", [error localizedDescription]);
	}
	
	return count;
}

- (CDFile *)cdCurrentFile
{
	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDFile" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"guid == %@", currentFileGuid]];
	NSError *error;
	NSArray *results = [getManagedObjectContext() executeFetchRequest:request error:&error];
	[request release];
	
	if (results)
	{
		if ([results count] >= 1)
		{
			return [results objectAtIndex:0];
		}
	}

	return nil;
}

- (void)setCdCurrentFile:(CDFile *)file
{
	[currentFileGuid release];
	currentFileGuid = [file.guid copy];
}

@end
