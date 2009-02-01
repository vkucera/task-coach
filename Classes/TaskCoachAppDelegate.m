//
//  TaskCoachAppDelegate.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright __MyCompanyName__ 2009. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "PositionStore.h"

@implementation TaskCoachAppDelegate

@synthesize window;
@synthesize mainController;

- (void)applicationDidFinishLaunching:(UIApplication *)application
{
	[window addSubview:mainController.view];
	
	NSArray *cachesPaths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
	NSString *cachesDir = [cachesPaths objectAtIndex:0];
	
	NSFileManager *fileManager = [NSFileManager defaultManager];
	if (![fileManager fileExistsAtPath:cachesDir])
	{
		[fileManager createDirectoryAtPath:cachesDir attributes:nil];
	}

	NSString *path = [cachesDir stringByAppendingPathComponent:@"positions.store"];

	if ([fileManager fileExistsAtPath:path])
	{
		PositionStore *store = [[PositionStore alloc] initWithFile:[cachesDir stringByAppendingPathComponent:@"positions.store"]];
		[store restore:mainController];
		[store release];
	}

	[fileManager release];
	
	[window makeKeyAndVisible];
}

- (void)dealloc
{
	[mainController release];
    [window release];

    [super dealloc];
}

- (void)applicationWillTerminate:(UIApplication *)application
{
	UIViewController *ctrl = [mainController topViewController];
	
	if ([ctrl respondsToSelector:@selector(willTerminate)])
		[ctrl performSelector:@selector(willTerminate)];
	
	
	NSArray *cachesPaths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
	NSString *cachesDir = [cachesPaths objectAtIndex:0];
	
	NSFileManager *fileManager = [NSFileManager defaultManager];
	if (![fileManager fileExistsAtPath:cachesDir])
	{
		[fileManager createDirectoryAtPath:cachesDir attributes:nil];
	}
	
	NSString *path = [cachesDir stringByAppendingPathComponent:@"positions.store"];
	[[PositionStore instance] save:path];

	[fileManager release];
}

@end
