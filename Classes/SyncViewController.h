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
	UIButton *cancelButton;

	NSString *host;
	NSInteger port;

	NSObject <State> *state;

	id target;
	SEL action;
}

@property (nonatomic, retain) IBOutlet UILabel *label;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView *activity;
@property (nonatomic, retain) IBOutlet UIProgressView *progress;
@property (nonatomic, retain) IBOutlet UITextField *password;
@property (nonatomic, retain) IBOutlet UIButton *cancelButton;

@property (nonatomic, retain) NSObject <State> *state;

- initWithTarget:(id)target action:(SEL)action host:(NSString *)host port:(NSInteger)port;

- (void)finished:(BOOL)ok;

- (IBAction)onCancel:(UIButton *)button;

@end
