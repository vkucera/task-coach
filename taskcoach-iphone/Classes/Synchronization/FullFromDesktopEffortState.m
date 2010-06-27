//
//  FullFromDesktopEffortState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 06/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "FullFromDesktopEffortState.h"
#import "EndState.h"
#import "SyncViewController.h"
#import "Configuration.h"
#import "CDEffort.h"
#import "CDTask.h"
#import "CDDomainObject+Addons.h"

@implementation FullFromDesktopEffortState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[FullFromDesktopEffortState alloc] initWithNetwork:network controller:controller] autorelease];
}

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	if ((self = [super initWithNetwork:network controller:controller]))
	{
		request = [[NSFetchRequest alloc] init];
		[request setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
	}

	return self;
}

- (void)dealloc
{
	[request release];

	[super dealloc];
}

- (void)activated
{
	[self startWithFormat:"ssszz" count:myController.effortCount];
}

- (void)onNewObject:(NSArray *)value
{
	CDEffort *effort = [NSEntityDescription insertNewObjectForEntityForName:@"CDEffort" inManagedObjectContext:getManagedObjectContext()];
	
	effort.file = [Configuration configuration].cdCurrentFile;
	effort.taskCoachId = [value objectAtIndex:0];
	effort.name = [value objectAtIndex:1];
	effort.status = [NSNumber numberWithInt:STATUS_NONE];
	effort.started = [self parseDate:[value objectAtIndex:3]];
	effort.ended = [self parseDate:[value objectAtIndex:4]];

	if ([value objectAtIndex:2] != [NSNull null])
	{
		[request setPredicate:[NSPredicate predicateWithFormat:@"taskCoachId == %@", [value objectAtIndex:2]]];
		NSError *error;
		NSArray *results = [getManagedObjectContext() executeFetchRequest:request error:&error];
	
		if (results)
		{
			assert([results count] == 1);
			effort.task = [results objectAtIndex:0];
		}
		else
		{
			NSLog(@"Could not fetch effort task: %@", [error localizedDescription]);
		}
	}

	[myController increment];
	[self sendFormat:"i" values:[NSArray arrayWithObject:[NSNumber numberWithInt:1]]];
}

- (void)onFinished
{
	myController.state = [EndState stateWithNetwork:myNetwork controller:myController];
}

@end
