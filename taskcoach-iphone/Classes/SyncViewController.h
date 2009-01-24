//
//  SyncViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "Network.h"
#import "State.h"

@interface SyncViewController : UIViewController <NetworkDelegate>
{
	UILabel *label;
	UIActivityIndicatorView *activity;
	UIProgressView *progress;
	UITextField *password;

	NSObject <State> *state;
}

@property (nonatomic, retain) IBOutlet UILabel *label;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView *activity;
@property (nonatomic, retain) IBOutlet UIProgressView *progress;
@property (nonatomic, retain) IBOutlet UITextField *password;

@property (nonatomic, retain) NSObject <State> *state;

- init;

@end
